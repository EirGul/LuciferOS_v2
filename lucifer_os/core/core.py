from dataclasses import dataclass, replace

from lucifer_os.audit.trace import AuditEvent, AuditTrace
from lucifer_os.core.config import ConfigLoader
from lucifer_os.core.diagnostics import DiagnosticsService
from lucifer_os.permissions.engine import PermissionEngine
from lucifer_os.permissions.risk import PermissionDecision
from lucifer_os.planning.plan import Plan
from lucifer_os.planning.planner import Planner
from lucifer_os.platform.detection import detect_platform
from lucifer_os.providers.base import Provider
from lucifer_os.providers.offline import OfflineProvider
from lucifer_os.response.builder import ResponseBuilder
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
    def __init__(self, primary_provider: Provider | None = None, project_root: str = '.'):
        self.project_root = project_root
        self.router = IntentRouter()
        self.planner = Planner()
        self.permission_engine = PermissionEngine()
        self.response_builder = ResponseBuilder()
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

        response = self._create_response(
            request=request,
            intent=intent,
            plan=plan,
            permission=permission,
            trace=trace,
        )

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
        intent: Intent,
        plan: Plan,
        permission: PermissionDecision,
        trace: AuditTrace,
    ) -> LuciferResponse:
        if plan.type == 'execute_command' and intent.name == 'status' and permission.allowed:
            return self._create_status_response(trace=trace)

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

    def _create_status_response(self, trace: AuditTrace) -> LuciferResponse:
        config = ConfigLoader(project_root=self.project_root).load()
        platform = detect_platform()
        diagnostics = DiagnosticsService(
            config=config,
            platform=platform,
            active_provider=self.primary_provider,
        )
        status = diagnostics.status()

        trace.record(
            event_type='diagnostics_created',
            message='Diagnostics status created.',
            metadata={
                'active_provider': status.active_provider,
                'provider_health': str(status.provider_health),
            },
        )

        visual_text = (
            f'LuciferOS status\n'
            f'Project: {status.project_name}\n'
            f'Platform: {status.platform_system} {status.platform_release}\n'
            f'Python: {status.python_version}\n'
            f'Active provider: {status.active_provider}\n'
            f'Provider health: {status.provider_health}\n'
            f'Default provider: {status.default_provider}\n'            f'Ollama model: {status.ollama_model}\n'
            f'Performance mode: {status.performance_mode}\n'
            f'Audit enabled: {status.audit_enabled}'
        )

        return self.response_builder.build(
            voice_summary=f'LuciferOS kjører. Aktiv provider er {status.active_provider}.',
            visual_text=visual_text,
            visual_channel='cli',
            requires_confirmation=False,
            risk_level=1,
            action='status',
        )
