from lucifer_os.permissions.risk import PermissionDecision, RiskLevel


class PermissionEngine:
    def evaluate(self, risk_level: int) -> PermissionDecision:
        risk = RiskLevel(risk_level)

        if risk <= RiskLevel.SAFE_LOCAL:
            return PermissionDecision(
                allowed=True,
                requires_confirmation=False,
                risk_level=risk,
                reason='Risk level is allowed without confirmation.',
            )

        return PermissionDecision(
            allowed=False,
            requires_confirmation=True,
            risk_level=risk,
            reason='Risk level requires explicit confirmation before execution.',
        )
