from app.state.competitor_state import CompetitorState
from app.schemas.competitors import CompetitorPayload


class CompetitorService:
    def __init__(self):
        self.state = CompetitorState()

    def update_competitor(self, competitor: CompetitorPayload):
        self.state.update_competitor(competitor)

    def get_competitors(self):
        return self.state.get_all()

    def clear(self):
        self.state.clear()