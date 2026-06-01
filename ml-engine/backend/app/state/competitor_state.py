from app.schemas.competitors import CompetitorPayload


class CompetitorState:
    def __init__(self):
        self.competitors: dict[str, CompetitorPayload] = {}

    def update_competitor(self, competitor: CompetitorPayload):
        self.competitors[competitor.car_id] = competitor

    def get_all(self):
        return [
            competitor.model_dump()
            for competitor in self.competitors.values()
        ]

    def clear(self):
        self.competitors.clear()