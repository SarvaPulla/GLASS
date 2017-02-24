from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import xmltodict, json
from json import dumps,loads
import requests, urllib2
from requests.auth import HTTPBasicAuth
from django.contrib.auth import authenticate
from suds.client import Client
from django.core import serializers
from datetime import datetime, timedelta
from tethys_sdk.gizmos import TimeSeries, SelectInput, DatePicker, TextInput
from tethys_sdk.gizmos import MapView, MVDraw, MVView, MVLayer, MVLegendClass, GoogleMapView
from owslib.waterml.wml11 import WaterML_1_1 as wml11
import logging, calendar
from utilities import *

logging.getLogger('suds.client').setLevel(logging.CRITICAL)
@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    # view_options = MVView(
    #     projection='EPSG:4326',
    #     center=[-70.6,18.75],
    #     zoom=8,
    #     maxZoom=18,
    #     minZoom=2
    # )
    #
    # # Define GeoServer Layer
    # ozama_layer = MVLayer(source='ImageWMS',
    #                           options={'url': 'http://tethys.byu.edu:8181/geoserver/wms',
    #                                    'params': {'LAYERS': 'spt-30935191ace55f90bd1e61456f1ef016:dominican_republic-ozama-drainage_line'},
    #                                    'serverType': 'geoserver'},
    #                             legend_title='Ozama'
    #                           )
    # haina_layer = MVLayer(source='ImageWMS',
    #                       options={'url': 'http://tethys.byu.edu:8181/geoserver/wms',
    #                                'params': {
    #                                    'LAYERS': 'spt-d7a8ccd9e71e5d7f9e8ecc2985206c8b:dominican_republic-haina-drainage_line'},
    #                                'serverType': 'geoserver'},
    #                       legend_title='Haina'
    #                       )
    # dr_layer = MVLayer(source='ImageWMS',
    #                       options={'url': 'http://tethys.byu.edu:8181/geoserver/wms',
    #                                'params': {
    #                                    'LAYERS': 'catalog:DominicanRepublic'},
    #                                'serverType': 'geoserver'},
    #                    legend_title='DR'
    #                       )
    # # Define map view options
    # map_view_options = MapView(
    #     height='600px',
    #     width='100%',
    #     controls=['ZoomSlider'],
    #     layers=[ozama_layer,haina_layer,dr_layer],
    #     view=view_options,
    #     basemap='Bing'
    # )

    context = {}

    return render(request, 'glass/home.html', context)

def details(request):
    """
    Controller for the app home page.
    """
    context = {}
    if request.GET['service'] == 'SFPT':
        sfpt = request.GET['service']
        comid = request.GET['comid']
        watershed = request.GET['watershed']
        subbasin = request.GET['subbasin']

        # waterml_url = 'http://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder=most_recent&stat_type=mean'.format(watershed,subbasin,comid)
        waterml_url = 'http://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder=most_recent&stat_type=mean&token=72b145121add58bcc5843044d9f1006d9140b84b'.format(watershed,subbasin,comid)
        # print waterml_url
        data = get_wml_values(waterml_url)


        timeseries_plot = TimeSeries(
            height='400px',
            width='100%',
            engine='highcharts',
            title='Streamflow at reach '+comid+ ' in '+subbasin,
            y_axis_title='Streamflow',
            y_axis_units='cfs',
            series=[{
                'name': 'Streamflow',
                'data': data
            }]
        )

        # compare_url = "/apps/glass/details/?comid=" + comid + "&watershed=" + watershed + "&subbasin=" + subbasin+"&service=SFPT"
        compare_data = {"comid":comid,"watershed":watershed,"subbasin":subbasin,"service":"SFTP"}
        request.session['compare_data'] = compare_data

        context = {"comid":comid,"watershed":watershed,"subbasin":subbasin,"sfpt":sfpt,"compare_data":compare_data,"timeseries_plot":timeseries_plot}



    return render(request, 'glass/details.html', context)

def compare(request):
    """
    Controller for the app home page.
    """

    context = {}

    return render(request, 'glass/compare.html', context)

def details2(request):
    context = {}
    if request.GET['service'] == 'SFPT':
        series1 = request.session['compare_data']
        comid1 = series1['comid']
        watershed1 = series1['watershed']
        subbasin1 = series1['subbasin']
        service1 = series1['service']
        comid2 = request.GET['comid2']
        watershed2 = request.GET['watershed2']
        subbasin2 = request.GET['subbasin2']
        service2 = request.GET['service']
        series2 = {"comid":comid2,"watershed":watershed2,"subbasin":subbasin2,"service":"SFTP"}

        wml_url1 = 'http://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder=most_recent&stat_type=mean&token=72b145121add58bcc5843044d9f1006d9140b84b'.format(
             watershed1, subbasin1, comid1)
        wml_url2 = 'http://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder=most_recent&stat_type=mean&token=72b145121add58bcc5843044d9f1006d9140b84b'.format(
            watershed2, subbasin2, comid2)
        series1_data = get_wml_values(wml_url1)
        series2_data = get_wml_values(wml_url2)
        timeseries_plot = TimeSeries(
            height='400px',
            width='100%',
            engine='highcharts',
            title='Streamflow at reach ' + comid1 +'&'+comid2 + ' in ' + subbasin1+'&'+subbasin2,
            y_axis_title='Streamflow',
            y_axis_units='cfs',
            series=[{
                'name': 'Series 1:'+subbasin1+' '+comid1,
                'data': series1_data
            },
                {
                    'name': 'Series 2:'+subbasin2+' '+comid2,
                    'data': series2_data
                }]
        )


        context = {"series1":series1,"series2":series2,"sftp":service2,"timeseries_plot":timeseries_plot}
    if request.GET['service'] == 'SOAP':
        series1 = request.session['compare_data']
        comid1 = series1['comid']
        watershed1 = series1['watershed']
        subbasin1 = series1['subbasin']
        service1 = series1['service']
        wml_url1 = 'http://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder=most_recent&stat_type=mean&token=72b145121add58bcc5843044d9f1006d9140b84b'.format(
            watershed1, subbasin1, comid1)
        series1_data = get_wml_values(wml_url1)




        hs_url = request.GET['hsurl']
        site_name = request.GET['sitename']
        site_code = request.GET['sitecode']
        network = request.GET['network']
        hidenav = request.GET['hidenav']
        service2 = request.GET['service']
        service = service2

        soap_obj = {}
        soap_obj["url"] = hs_url

        client = Client(hs_url)
        client.set_options(port='WaterOneFlow')
        site_desc = network + ":" + site_code
        soap_obj["site"] = site_desc
        soap_obj["network"] = network
        site_info = client.service.GetSiteInfo(site_desc)
        site_info = site_info.encode('utf-8')
        info_dict = xmltodict.parse(site_info)
        info_json_object = json.dumps(info_dict)
        info_json = json.loads(info_json_object)
        site_variables = []
        site_object_info = info_json['sitesResponse']['site']['seriesCatalog']
        try:
            site_object = info_json['sitesResponse']['site']['seriesCatalog']['series']
        except KeyError:
            error_message = "Site Details do not exist"
            context = {"site_name": site_name, "site_code": site_code, "service": service,
                       "error_message": error_message}
            return render(request, 'servir/error.html', context)
        graph_variables = []
        var_json = []
        if type(site_object) is list:
            count = 0
            for i in site_object:
                var_obj = {}
                count = count + 1

                variable_name = i['variable']['variableName']
                variable_id = i['variable']['variableCode']['@variableID']
                variable_text = i['variable']['variableCode']['#text']
                var_obj["variableName"] = variable_name
                var_obj["variableID"] = variable_id
                # value_type = i['variable']['valueType']
                value_count = i['valueCount']
                # data_type = i['variable']['dataType']
                # unit_name = i['variable']['unit']['unitName']
                # unit_type = i['variable']['unit']['unitType']
                # unit_abbr = i['variable']['unit']['unitAbbreviation']
                # unit_code = i['variable']['unit']['unitCode']
                # time_support = i['variable']['timeScale']['timeSupport']
                # time_support_name = i['variable']['timeScale']['unit']['unitName']
                # time_support_type = i['variable']['timeScale']['unit']['unitAbbreviation']
                begin_time = i["variableTimeInterval"]["beginDateTimeUTC"]
                begin_time = begin_time.split("T")
                begin_time = str(begin_time[0])
                end_time = i["variableTimeInterval"]["endDateTimeUTC"]
                end_time = end_time.split("T")
                end_time = str(end_time[0])
                var_obj["startDate"] = begin_time
                var_obj["endDate"] = end_time
                # print begin_time,end_time
                method_id = i["method"]["@methodID"]
                # method_desc = i["method"]["methodDescription"]
                # source_id = i["source"]["@sourceID"]
                # source_org = i["source"]["organization"]
                # source_desc = i["source"]["sourceDescription"]
                # qc_code = i["qualityControlLevel"]["qualityControlLevelCode"]
                # qc_id = i["qualityControlLevel"]["@qualityControlLevelID"]
                # qc_definition = i["qualityControlLevel"]["definition"]
                # print variable_name,variable_id, source_id,method_id, qc_code
                variable_string = str(
                    count) + '. Variable Name:' + variable_name + ',' + 'Count: ' + value_count + ',Variable ID:' + variable_id + ', Start Date:' + begin_time + ', End Date:' + end_time
                # value_string = variable_id,variable_text,source_id,method_id,qc_code, variable_name
                value_list = [variable_text, method_id]
                value_string = str(value_list)
                graph_variables.append([variable_string, value_string])
                var_json.append(var_obj)
                # print variable_name, variable_id, value_type, data_type, unit_name,unit_type, unit_abbr,unit_abbr,unit_code, time_support, time_support_name, time_support_type
        else:
            var_obj = {}
            variable_name = site_object['variable']['variableName']
            variable_id = site_object['variable']['variableCode']['@variableID']
            variable_text = site_object['variable']['variableCode']['#text']
            value_count = site_object['valueCount']

            # value_type = site_object['variable']['valueType']
            # data_type = site_object['variable']['dataType']
            # unit_name = site_object['variable']['unit']['unitName']
            # unit_type = site_object['variable']['unit']['unitType']
            # unit_abbr = site_object['variable']['unit']['unitAbbreviation']
            # unit_code = site_object['variable']['unit']['unitCode']
            # time_support = site_object['variable']['timeScale']['timeSupport']
            # time_support_name = site_object['variable']['timeScale']['unit']['unitName']
            # time_support_type = site_object['variable']['timeScale']['unit']['unitAbbreviation']
            begin_time = site_object["variableTimeInterval"]["beginDateTimeUTC"]
            begin_time = begin_time.split("T")
            begin_time = str(begin_time[0])
            end_time = site_object["variableTimeInterval"]["endDateTimeUTC"]
            end_time = end_time.split("T")
            end_time = str(end_time[0])
            method_id = site_object["method"]["@methodID"]
            # method_desc = site_object["method"]["methodDescription"]
            # source_id = site_object["source"]["@sourceID"]
            # source_org = site_object["source"]["organization"]
            # source_desc = site_object["source"]["sourceDescription"]
            # qc_code = site_object["qualityControlLevel"]["qualityControlLevelCode"]
            # qc_id = site_object["qualityControlLevel"]["@qualityControlLevelID"]
            # qc_definition = site_object["qualityControlLevel"]["definition"]
            variable_string = '1. Variable Name:' + variable_name + ',' + 'Count: ' + value_count + ',Variable ID:' + variable_id + ', Start Date:' + begin_time + ', End Date:' + end_time
            # print variable_name, variable_id, source_id, method_id, qc_code
            value_list = [variable_text, method_id]
            value_string = str(value_list)
            var_obj["variableName"] = variable_name
            var_obj["variableID"] = variable_id
            var_obj["startDate"] = begin_time
            var_obj["endDate"] = end_time
            var_json.append(var_obj)
            graph_variables.append([variable_string, value_string])

        # print site_values
        # values = client.service.GetSiteInfo(site_desc)
        # print values
        select_soap_variable = SelectInput(display_text='Select Variable', name="select_var", multiple=False,
                                           options=graph_variables)

        t_now = datetime.now()
        now_str = "{0}-{1}-{2}".format(t_now.year, check_digit(t_now.month), check_digit(t_now.day))
        start_date = DatePicker(name='start_date',
                                display_text='Start Date',
                                autoclose=True,
                                format='yyyy-mm-dd',
                                start_view='month',
                                today_button=True,
                                initial=now_str)
        end_date = DatePicker(name='end_date',
                              display_text='End Date',
                              autoclose=True,
                              format='yyyy-mm-dd',
                              start_view='month',
                              today_button=True,
                              initial=now_str)

        select_variable = []
        graphs_object = {}
        json.JSONEncoder.default = lambda self, obj: (obj.isoformat() if isinstance(obj, datetime) else None)
        soap_obj["var_list"] = var_json
        request.session['soap_obj'] = soap_obj


        context = {"series1":series1,"soap":service2,"site_name":site_name,"site_code":site_code,"network":network,"hs_url":hs_url,"service":service,"hidenav":hidenav,"select_soap_variable":select_soap_variable,"select_variable":select_variable,"start_date":start_date,"end_date":end_date,"graphs_object":graphs_object,"soap_obj":soap_obj}


    return render(request,'glass/details2.html',context)

def soap_var(request):
    var_object = None
    if 'soap_obj' in request.session:
        var_object = request.session['soap_obj']
    return JsonResponse(var_object)

def soap_api(request):
    soap_object = None
    if 'soap_obj' in request.session:
        soap_object = request.session['soap_obj']

        url = soap_object['url']
        site_desc = soap_object['site']
        network = soap_object['network']
        variable =  request.POST['select_var']
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        variable =  str(variable)
        variable =  variable.replace("[","").replace("]","").replace("u","").replace(" ","").replace("'","")
        variable = variable.split(',')
        variable_text = variable[0]
        variable_method = variable[1]
        variable_desc = network+':'+variable_text
        client = Client(url)
        values = client.service.GetValues(site_desc,variable_desc,start_date,end_date,"")
        values_dict = xmltodict.parse(values)
        values_json_object = json.dumps(values_dict)
        values_json = json.loads(values_json_object)
        times_series = values_json['timeSeriesResponse']['timeSeries']
        if times_series['values'] is not None:
            graph_json = {}
            graph_json["variable"] = times_series['variable']['variableName']
            graph_json["unit"] = times_series['variable']['unit']['unitAbbreviation']
            graph_json["title"] = site_desc + ':' + times_series['variable']['variableName']
            for j in times_series['values']:
                data_values = []
                if j == "value":
                    if type((times_series['values']['value'])) is list:
                        count = 0
                        for k in times_series['values']['value']:
                            try:
                                if k['@methodCode'] == variable_method:
                                    count = count + 1
                                    time = k['@dateTimeUTC']
                                    time1 = time.replace("T", "-")
                                    time_split = time1.split("-")
                                    year = int(time_split[0])
                                    month = int(time_split[1])
                                    day = int(time_split[2])
                                    hour_minute = time_split[3].split(":")
                                    hour = int(hour_minute[0])
                                    minute = int(hour_minute[1])
                                    value = float(str(k['#text']))
                                    date_string = datetime(year, month, day, hour, minute)
                                    time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
                                    data_values.append([time_stamp, value])
                                    data_values.sort()
                                graph_json["values"] = data_values
                                graph_json["count"] = count
                            except KeyError:
                                count = count + 1
                                time = k['@dateTimeUTC']
                                time1 = time.replace("T", "-")
                                time_split = time1.split("-")
                                year = int(time_split[0])
                                month = int(time_split[1])
                                day = int(time_split[2])
                                hour_minute = time_split[3].split(":")
                                hour = int(hour_minute[0])
                                minute = int(hour_minute[1])
                                value = float(str(k['#text']))
                                date_string = datetime(year, month, day, hour, minute)
                                time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
                                data_values.append([time_stamp, value])
                                data_values.sort()
                            graph_json["values"] = data_values
                            graph_json["count"] = count
                    else:
                        try:
                            if times_series['values']['value']['@methodCode'] == variable_method:
                                time = times_series['values']['value']['@dateTimeUTC']
                                time1 = time.replace("T", "-")
                                time_split = time1.split("-")
                                year = int(time_split[0])
                                month = int(time_split[1])
                                day = int(time_split[2])
                                hour_minute = time_split[3].split(":")
                                hour = int(hour_minute[0])
                                minute = int(hour_minute[1])
                                value = float(str(times_series['values']['value']['#text']))
                                date_string = datetime(year, month, day, hour, minute)
                                time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
                                data_values.append([time_stamp, value])
                                data_values.sort()
                                graph_json["values"] = data_values
                                graph_json["count"] = 1
                        except KeyError:
                            time = times_series['values']['value']['@dateTimeUTC']
                            time1 = time.replace("T", "-")
                            time_split = time1.split("-")
                            year = int(time_split[0])
                            month = int(time_split[1])
                            day = int(time_split[2])
                            hour_minute = time_split[3].split(":")
                            hour = int(hour_minute[0])
                            minute = int(hour_minute[1])
                            value = float(str(times_series['values']['value']['#text']))
                            date_string = datetime(year, month, day, hour, minute)
                            time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
                            data_values.append([time_stamp, value])
                            data_values.sort()
                            graph_json["values"] = data_values
                            graph_json["count"] = 1

    # request.session['graph_obj'] = graph_json
    series1 = request.session['compare_data']
    comid1 = series1['comid']
    watershed1 = series1['watershed']
    subbasin1 = series1['subbasin']
    service1 = series1['service']
    wml_url1 = 'http://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder=most_recent&stat_type=mean&token=72b145121add58bcc5843044d9f1006d9140b84b'.format(
        watershed1, subbasin1, comid1)
    series1_data = get_wml_values(wml_url1)

    graphit = {'soap':graph_json,'sfpt':series1_data}

    return JsonResponse(graphit)

def check_digit(num):
    num_str = str(num)
    if len(num_str) < 2:
        num_str = '0' + num_str
    return num_str