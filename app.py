from collections import OrderedDict
from datetime import timedelta
import requests

from models import Camp, CampArea, Equipment, ResourceCategory, Site, SiteAvailability


ENDPOINTS = {
    'LIST_RESOURCECATEGORY': 'https://wisconsin.goingtocamp.com/api/resourcecategory',
    'LIST_EQUIPMENT': 'https://wisconsin.goingtocamp.com/api/equipment',
    'LIST_RESOURCESTATUS': 'https://wisconsin.goingtocamp.com/api/availability/resourcestatus',
    'MAPDATA': 'https://wisconsin.goingtocamp.com/api/maps/mapdatabyid',
    'LIST_CAMPGROUNDS': 'https://wisconsin.goingtocamp.com/api/resourcelocation/rootmaps',
    'SITE_DETAILS': 'https://wisconsin.goingtocamp.com/api/resource/details',
    # 'CAMP_DETAILS_SINGLE': 'https://wisconsin.goingtocamp.com/api/resourcelocation/locationdetails',
    'CAMP_DETAILS_ALL': 'https://wisconsin.goingtocamp.com/api/resourcelocation',
    'DAILY_AVAILABILITY': 'https://wisconsin.goingtocamp.com/api/availability/resourcedailyavailability',
}

CAMP_DETAILS_BY_LOCATIONID = {}


def get_json(endpoint, params=None):
    return requests.get(ENDPOINTS[endpoint], params=params).json()


def post_json(endpoint, data=None):
    return requests.post(ENDPOINTS[endpoint], headers={'Content-Type': 'application/json'}, json=data).json()


def get_reservation_link(party_size, start_date, end_date, camp_area, resource_location_id, equipment_id, sub_equipment_id):
    """
    Web link at which a reservation could be made for the specified search
    :param party_size:
    :param start_date:
    :param end_date:
    :param camp_area:
    :param resource_location_id:
    :param equipment_id:
    :param sub_equipment_id:
    :return:
    """
    return\
        'https://wisconsin.goingtocamp.com/create-booking/results?mapId=%s&bookingCategoryId=0&startDate=%s&endDate=%s&isReserving=true&equipmentId=%s&subEquipmentId=%s&partySize=%s&resourceLocationId=%s'\
        %(camp_area.map_id, start_date.isoformat(), end_date.isoformat(), equipment_id, sub_equipment_id, party_size, resource_location_id)


def list_resource_categorys():
    """
    Retrieve all known Resource Categories
    :return:
    """
    return [ResourceCategory(e['resourceCategoryId'],e['localizedValues'][0]['name']) for e in get_json('LIST_RESOURCECATEGORY')]


def list_equipments():
    """
    Retrieve all known Equipment
    :return:
    """
    equipments = []
    equipment_all = sorted(get_json('LIST_EQUIPMENT'), key=lambda e: e['order'])
    for category in equipment_all:
        equipment = category['subEquipmentCategories']
        equipments.extend([Equipment(category['equipmentCategoryId'],e['subEquipmentCategoryId'],e['localizedValues'][0]['name']) for e in equipment])
    return equipments


def list_camps(resource_category_id):
    """
    Retrieve Camps which can host the selected Resource Category
    :param resource_category_id:
    :return:
    """
    camps = []
    for camp in get_json('LIST_CAMPGROUNDS'):
        if camp['resourceLocationId'] and resource_category_id in camp['resourceCategoryIds']:
            camps.append(Camp(camp['mapId'], camp['resourceLocationId'],camp['resourceLocationLocalizedValues']['en-US']))
    return camps

def init_camp_details():
    if(len(CAMP_DETAILS_BY_LOCATIONID) is 0):
        all_camp_details = get_json('CAMP_DETAILS_ALL')
        for camp_details in all_camp_details:
            CAMP_DETAILS_BY_LOCATIONID[camp_details['resourceLocationId']] = camp_details['localizedValues']

def get_camp_description(resource_location_id):
    """
    Get longform description of this Camp
    :param resource_location_id:
    :return:
    """
    init_camp_details()
    return CAMP_DETAILS_BY_LOCATIONID[resource_location_id][0]['description']
    # return get_json('CAMP_DETAILS_SINGLE', {'resourceLocationId':resource_location_id})['localizedDetails'][0]['description']


def get_site_description(site):
    """
    Get longform description of this Site
    """
    return get_json('SITE_DETAILS', {'resourceId':site.resource_id})['localizedValues'][0]
    #['description']


def list_camp_areas(camp, start_date, end_date, equipment_type):
    """
    Retrieve Areas within a Camp which can host the selected Equipment within a date range
    :param camp:
    :param start_date:
    :param end_date:
    :param equipment_type:
    :return:
    """
    data = {
       'mapId':camp.map_id,
       'bookingCategoryId':0,
       'startDate':start_date.isoformat(),
       'endDate':end_date.isoformat(),
       'isReserving':True,
       'getDailyAvailability':True,
       'partySize':1,
       'equipmentId':equipment_type,
       'subEquipmentId':equipment_type,
       'generateBreadcrumbs':False,
    }
    results = post_json('MAPDATA', data)
    camp_areas = []
    for map_id, info in results['mapLinkLocalizedValues'].items():
        for entry in info:
            camp_areas.append(CampArea(map_id, entry['title'],entry['description']))
    return camp_areas


def list_sites(camp_area, start_date, end_date, equipment_type):
    """
    Retrieve Sites within a Camp Area which can host the selected Equipment within a date range
    :param camp_area:
    :param start_date:
    :param end_date:
    :param equipment_type:
    :return:
    """
    data = {
       'mapId':camp_area.map_id,
       'bookingCategoryId':0,
       'startDate':start_date.isoformat(),
       'endDate':end_date.isoformat(),
       'isReserving':True,
       'getDailyAvailability':True,
       'partySize':1,
       'equipmentId':equipment_type,
       'subEquipmentId':equipment_type,
       'generateBreadcrumbs':False,
    }
    results = post_json('MAPDATA', data)
    sites = []
    for entry in results['resourcesOnMap']:
        sites.append(Site(entry['resourceId'], entry['localizedValues'][0]['name'],entry['localizedValues'][0]['description']))
    sites.sort(key=lambda site: site.name.zfill(3))
    return sites


def list_site_availability(camp_area, start_date, end_date, equipment_type):
    """
    Retrieve the Availability for all Sites in a Camp Area which can host the selected Equipment within a date range
    :param camp_area:
    :param start_date:
    :param end_date:
    :param equipment_type:
    :return:
    """
    data = {
       'mapId':camp_area.map_id,
       'bookingCategoryId':0,
       'startDate':start_date.isoformat(),
       'endDate':end_date.isoformat(),
       'isReserving':True,
       'getDailyAvailability':True,
       'partySize':1,
       'equipmentId':equipment_type,
       'subEquipmentId':equipment_type,
       'generateBreadcrumbs':False,
    }
    results = post_json('MAPDATA', data)
    sites_availability = {}
    for entry in results['resourcesOnMap']:
        site = Site(entry['resourceId'], entry['localizedValues'][0]['name'],entry['localizedValues'][0]['description'])
        allowed_equipment = [Equipment(e['item1'],e['item2'], None) for e in entry['allowedEquipment']]
        availability = [
            SiteAvailability(site, e['availability'], allowed_equipment)
            for e in results['resourceAvailabilityMap'][str(site.resource_id)]
        ]
        sites_availability[site] = availability
    return OrderedDict(sorted(sites_availability.items(), key=lambda sa: sa[0].name.zfill(3)))