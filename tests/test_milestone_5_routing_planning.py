from lucifer_os.planning.planner import Planner
from lucifer_os.routing.router import IntentRouter


def test_router_routes_empty_input_to_unknown():
    router = IntentRouter()

    intent = router.route('   ')

    assert intent.type == 'unknown'
    assert intent.name == 'empty_input'
    assert intent.confidence == 1.0


def test_router_routes_status_as_command():
    router = IntentRouter()

    intent = router.route('status')

    assert intent.type == 'command'
    assert intent.name == 'status'
    assert intent.confidence == 1.0


def test_router_routes_unknown_text_as_conversation():
    router = IntentRouter()

    intent = router.route('hva mener du om denne arkitekturen?')

    assert intent.type == 'conversation'
    assert intent.name == 'free_chat'
    assert intent.confidence == 0.7


def test_router_routes_confirmation():
    router = IntentRouter()

    intent = router.route('ja utfør')

    assert intent.type == 'confirmation'
    assert intent.name == 'confirm_action'


def test_planner_creates_response_plan_for_conversation():
    router = IntentRouter()
    planner = Planner()

    intent = router.route('hva tenker du?')
    plan = planner.create_plan(intent)

    assert plan.type == 'respond'
    assert plan.intent_name == 'free_chat'
    assert plan.risk_level == 0
    assert plan.requires_permission is False


def test_planner_creates_command_plan_for_safe_command():
    router = IntentRouter()
    planner = Planner()

    intent = router.route('status')
    plan = planner.create_plan(intent)

    assert plan.type == 'execute_command'
    assert plan.intent_name == 'status'
    assert plan.risk_level == 1
    assert plan.requires_permission is False
