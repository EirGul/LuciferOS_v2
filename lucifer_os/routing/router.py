from lucifer_os.routing.intent import Intent


class IntentRouter:
    def route(self, text: str) -> Intent:
        raw_text = text
        normalized_text = text.strip().lower()

        if not normalized_text:
            return Intent(
                type='unknown',
                name='empty_input',
                confidence=1.0,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        if normalized_text in {'ja', 'ja utfør', 'bekreft', 'bekreft ja utfør'}:
            return Intent(
                type='confirmation',
                name='confirm_action',
                confidence=1.0,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        if normalized_text in {'nei', 'avbryt', 'stopp'}:
            return Intent(
                type='confirmation',
                name='cancel_action',
                confidence=1.0,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        if normalized_text in {'status', 'hjelp', 'vis providers', 'vis tools'}:
            return Intent(
                type='command',
                name=normalized_text.replace(' ', '_'),
                confidence=1.0,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        return Intent(
            type='conversation',
            name='free_chat',
            confidence=0.7,
            raw_text=raw_text,
            normalized_text=normalized_text,
        )
