from sttapp.proposals.models import Itinerary


def generate_itinerary_list(start_dt, end_dt):

    for i in range((end_dt-start_dt).days):
        yield Itinerary(day_number=i)
