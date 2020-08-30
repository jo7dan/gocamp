from console import *
from datetime import date


def search(party_size, year, start_month, start_day, end_month, end_day, resource_category, equipment, max_camps=0):
    # sanity check
    start_date = datetime.datetime(year, start_month, start_day)
    end_date = datetime.datetime(year, end_month, end_day)
    dates = [(start_date + datetime.timedelta(days=x)).strftime('%y-%b-%d') for x in range(0, (end_date-start_date).days)]
    if len(dates) == 0:
        raise Exception("must stay at least 1 night")
    equipment_id_subid = (equipment.category_id, equipment.subcategory_id)
    # search
    print('\n\n')
    #print('%s, %s, %s, %s ppl' %(dates,resource_category,equipment,party_size))
    if max_camps:
        camps = list_camps(resource_category.resource_id)[:max_camps]
    else:
        camps = list_camps(resource_category.resource_id)
    
    for camp in camps:
        output = []
        for camp_area in list_camp_areas(camp, start_date, end_date, equipment.subcategory_id):
            available_sites = []
            for site, site_availabilitys in list_site_availability(camp_area, start_date, end_date, equipment.subcategory_id).items():
                if is_available(site, dates, site_availabilitys, equipment_id_subid):
                    available_sites.append(site.name)
            if(len(available_sites)):
                output.append('        [%s to %s]' %(start_date.date().isoformat(), end_date.date().isoformat()))
                output.append('    %s:(%s): %s' %(camp, camp_area, available_sites))
                reservation_link = get_reservation_link(party_size, start_date, end_date, camp_area, camp.resource_location_id, equipment.category_id, equipment.subcategory_id)
                output.append('    %s' %reservation_link)
                output.append('\n')
        if output:
            #print('  %s'%get_camp_description(camp.resource_location_id))
            for line in output:
                print(line)

def search_weekends(party_size, year, start_month, start_day, end_month, end_day, resource_category, equipment, max_camps=0):
    # iso weekends are 5,6,7 for Friday, Saturday, Sunday respectively
    start_date = datetime.datetime(year, start_month, start_day, 7, tzinfo=datetime.timezone.utc)
    end_date = datetime.datetime(year, end_month, end_day, 7, tzinfo=datetime.timezone.utc)
    next_friday = start_date + datetime.timedelta( (4-start_date.weekday()) % 7)

    if next_friday>end_date:
        raise Exception("End date is before a weekend")

    while next_friday.toordinal()<end_date.toordinal():
        sunday = date.fromordinal(next_friday.toordinal() + 2)
        #print('%s to %s' %(next_friday, sunday))
        search(party_size, next_friday.year, next_friday.month, next_friday.day, sunday.month, sunday.day, resource_category, equipment, max_camps)
        next_friday = date.fromordinal(next_friday.toordinal() + 7)

if __name__ == '__main__':
    resource_categories = list_resource_categorys()
    resource_category = resource_categories[3] #campsite
    equipment_list = list_equipments()
    equipment = equipment_list[0] #Tent(s)
    party_size = 2
    year = 2020
    start_month = 9
    start_day = 25
    end_month = 10
    end_day = 27
    max_camps = 5

    # perform the search
    #search(party_size, year, start_month, start_day, end_month, end_day, resource_category, equipment, max_camps)
    search_weekends(party_size, year, start_month, start_day, end_month, end_day, resource_category, equipment, max_camps)