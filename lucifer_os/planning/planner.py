from lucifer_os.planning.plan import Plan
from lucifer_os.routing.intent import Intent


class Planner:
    def create_plan(self, intent: Intent) -> Plan:
        if intent.type == 'conversation':
            return Plan(
                type='respond',
                intent_name=intent.name,
                risk_level=0,
                requires_permission=False,
                description='Respond to user conversation.',
            )

        if intent.type == 'command':
            return Plan(
                type='execute_command',
                intent_name=intent.name,
                risk_level=1,
                requires_permission=False,
                description='Execute safe local command intent.',
            )

        if intent.type == 'confirmation':
            return Plan(
                type='handle_confirmation',
                intent_name=intent.name,
                risk_level=0,
                requires_permission=False,
                description='Handle confirmation or cancellation.',
            )

        return Plan(
            type='ask_clarification',
            intent_name=intent.name,
            risk_level=0,
            requires_permission=False,
            description='Ask user for clarification.',
        )
