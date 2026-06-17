from dataclasses import dataclass, replace

from lucifer_os.audit.trace import AuditEvent, AuditTrace
from lucifer_os.permissions.engine import PermissionEngine
from lucifer_os.permissions.risk import PermissionDecision
from lucifer_os.planning.plan import Plan
from lucifer_os.planning.planner import Planner
from lucifer_os.providers.base import Provider
from lucifer_os.providers.offline import OfflineProvider
from lucifer_os.response.response import LuciferResponse
from lucifer_os.routing.intent import Intent
from lucifer_os.routing.router import IntentRouter


@dataclass(frozen=True)
class CoreRequest:
    text: str


@dataclass(frozen=True)
class CoreResult:
    trace_id: str
    intent: Intent
    plan: Plan
    permission: PermissionDecision
    response: LuciferResponse
    audit_events: list[AuditEvent]


class LuciferCore:
    def __init__(self, primary_provider: Provider | None = None):
        self.router = IntentRouter()
        self.planner = Planner()
        self.permission_engine = PermissionEngine()
        self.offline_provider = OfflineProvider()
        self.primary_provider = primary_provider or self.offline_provider

    def handle(self, request: CoreRequest) -> CoreResult:
        trace = AuditTrace()
        trace.record(
            event_type='request_received',
            message='Core request received.',
            metadata={'text': request.text},
        )

        intent = self.router.route(request.text)
        trace.record(
            event_type='intent_routed',
            message='Intent routed.',
            metadata={'intent_type': intent.type, 'intent_name': intent.name},
        )

        plan = self.planner.create_plan(intent)
        trace.record(
            event_type='plan_created',
            message='Plan created.',
            metadata={'plan_type': plan.type, 'risk_level': str(plan.risk_level)},
        )

        permission = self.permission_engine.evaluate(plan.risk_level)
        trace.record(
            event_type='permission_evaluated',
            message='Permission evaluated.',
            metadata={
                'allowed': str(permission.allowed),
                'requires_confirmation': str(permission.requires_confirmation),
            },
        )

        response = self._create_response(request=request, plan=plan, permission=permission, trace=trace)

        response = replace(response, trace_id=trace.trace_id)
        trace.record(
            event_type='response_created',
            message='Response created.',
            metadata={'visual_channel': response.visual_channel},
        )

        return CoreResult(
            trace_id=trace.trace_id,
            intent=intent,
            plan=plan,
            permission=permission,
            response=response,
            audit_events=trace.events(),
        )

    def _create_response(
        self,
        request: CoreRequest,
        plan: Plan,
        permission: PermissionDecision,
        trace: AuditTrace,
    ) -> LuciferResponse:
        if plan.type != 'respond' or not permission.allowed:
            trace.record(
                event_type='provider_selected',
                message='Offline provider selected for non-response plan.',
                metadata={'provider': self.offline_provider.metadata().name},
            )
            return self.offline_provider.answer('')

        provider = self.primary_provider
        trace.record(
            event_type='provider_selected',
            message='Primary provider selected.',
            metadata={'provider': provider.metadata().name},
        )

        response = provider.answer(request.text)

        if response.voice_summary.startswith('OllamaProvider feilet trygt:'):
            trace.record(
                event_type='provider_fallback',
                message='Primary provider failed safely. Falling back to offline provider.',
                metadata={'fallback_provider': self.offline_provider.metadata().name},
            )
            return self.offline_provider.answer(request.text)

        return response
