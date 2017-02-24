/*****************************************************************************
 * FILE:    GLASS MAIN JS
 * DATE:    30 January 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var GLASS_PACKAGE = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var public_interface,
        baseLayer,
        current_layer,
        element,
        layers,
        layers_dict,
        map,
        dr_source,
        haina_source,
        ozama_source,
        popup,
        $SoapVariable,
        wmsLayer,
        wmsSource;



    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var ajax_call,
        generate_plot,
        init_map,
        init_jquery_var,
        init_events;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    init_jquery_var = function(){

    };

    init_map = function () {
        var projection = ol.proj.get('EPSG:4326');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
            })
        });
        var fullScreenControl = new ol.control.FullScreen();
        var view = new ol.View({
            center: [-70.6,18.75],
            projection: projection,
            zoom: 8
        });
        dr_source = new ol.source.TileWMS({
            url:'http://tethys.byu.edu:8181/geoserver/wms',
            params:{
                LAYERS:"catalog:DominicanRepublic"
            },
            crossOrigin: 'Anonymous'
        });
        var dr_layer = new ol.layer.Tile({
            source:dr_source
        });
        haina_source =  new ol.source.TileWMS({
            url:'http://tethys.byu.edu:8181/geoserver/wms',
            params:{
                LAYERS:"spt-d7a8ccd9e71e5d7f9e8ecc2985206c8b:dominican_republic-haina-drainage_line"
            },
            crossOrigin: 'Anonymous'
        });
        // var wms_url = 'http://preview.grid.unep.ch/geoserver/wfs?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&';
        var wms_source = new ol.source.TileWMS({
            url:'http://preview.grid.unep.ch/geoserver/wms',
            params:{
                LAYERS:"preview:fl_frequency"
                // VERSION:'1.3.0',
                // FORMAT:'image/png'
            },
            serverType: 'geoserver'
            // crossOrigin: 'Anonymous'
        });

        var wms_layer = new ol.layer.Tile({
            source:wms_source
        });
        // var jrc_source = new ol.source.TileWMS({
        //     url:'http://data.fmi.fi/fmi-apikey/456214d0-58a9-46e8-ac2d-a2d0ed1e8643/wms?',
        //     params:{
        //         LAYERS:"Precipitation"
        //         // VERSION:'1.3.0',
        //         // FORMAT:'image/png'
        //     },
        //     crossOrigin: 'Anonymous'
        // });
        // var jrc_layer = new ol.layer.Tile({
        //     source:jrc_source
        // });


        var haina_layer = new ol.layer.Tile({
            source:haina_source
        });
        ozama_source =  new ol.source.TileWMS({
            url:'http://tethys.byu.edu:8181/geoserver/wms',
            params:{
                LAYERS:"spt-30935191ace55f90bd1e61456f1ef016:dominican_republic-ozama-drainage_line"
            },
            crossOrigin: 'Anonymous'
        });
        var ozama_layer = new ol.layer.Tile({
            source:ozama_source
        });
        layers = [baseLayer,haina_layer,ozama_layer,dr_layer];
        layers_dict = {};

        map = new ol.Map({
            target: document.getElementById("map"),
            layers: layers,
             view: view
        });
        //


        map.addControl(new ol.control.ZoomSlider());
        map.addControl(fullScreenControl);
        map.crossOrigin = 'anonymous';
        element = document.getElementById('popup');

        popup = new ol.Overlay({
            element: element,
            positioning: 'bottom-center',
            stopEvent: true
        });
        map.addOverlay(popup);
        init_events();

    };
    // $('#close-modalViewCompare').on('click', function () {
    //         $('#modalViewCompare').modal('hide');
    //     });
    init_events = function(){
        (function () {
            var target, observer, config;
            // select the target node
            target = $('#app-content-wrapper')[0];

            observer = new MutationObserver(function () {
                window.setTimeout(function () {
                    map.updateSize();
                }, 350);
            });
            $(window).on('resize', function () {
                map.updateSize();
            });

            config = {attributes: true};

            observer.observe(target, config);
        }());

        map.on('singleclick', function(evt) {
            $(element).popover('destroy');

            if (map.getTargetElement().style.cursor == "pointer") {

                var clickCoord = evt.coordinate;
                popup.setPosition(clickCoord);

                var view = map.getView();
                var viewResolution = /** @type {number} */ (view.getResolution());

                var haina = haina_source.getGetFeatureInfoUrl(evt.coordinate, viewResolution, 'EPSG:4326', {'INFO_FORMAT': 'application/json'});
                var ozama = ozama_source.getGetFeatureInfoUrl(evt.coordinate, viewResolution, 'EPSG:4326', {'INFO_FORMAT': 'application/json'});
                var dr = dr_source.getGetFeatureInfoUrl(evt.coordinate, viewResolution, 'EPSG:4326', {'INFO_FORMAT': 'application/json'});
                var location = window.location.pathname;
                if (ozama) {
                    $.ajax({
                        type: "GET",
                        url: ozama,
                        dataType: 'json',
                        success: function (result) {
                            var comid = result["features"][0]["properties"]["COMID"];
                            var watershed = result["features"][0]["properties"]["watershed"];
                            var subbasin = result["features"][0]["properties"]["subbasin"];
                            var details_html;
                            if (location == "/apps/glass/compare/"){
                                details_html = "/apps/glass/details2/?comid2=" + comid + "&watershed2=" + watershed + "&subbasin2=" + subbasin+"&service=SFPT";
                            }else{
                                details_html = "/apps/glass/details/?comid=" + comid + "&watershed=" + watershed + "&subbasin=" + subbasin+"&service=SFPT";
                            }


                            $(element).popover({
                                'placement': 'top',
                                'html': true,
                                'content': '<table border="1"><tbody><tr><th>Watershed</th><th>Subbasin</th><th>Details</th></tr>' + '<tr><td>' + watershed + '</td><td>' + subbasin + '</td><td><button type="button" class="mod_link btn-primary" data-html="' + details_html + '" >Stream Details</button></td></tr>'
                            });

                            $(element).popover('show');
                            $(element).next().css('cursor', 'text');
                            $('.mod_link').on('click', function () {
                                var details_url = $(this).data('html');
                                window.open(details_url, "_blank");

                            });
                        }
                    });
                }
                if (haina) {
                    $.ajax({
                        type: "GET",
                        url: haina,
                        dataType: 'json',
                        success: function (result) {
                            var comid = result["features"][0]["properties"]["COMID"];
                            var watershed = result["features"][0]["properties"]["watershed"];
                            var subbasin = result["features"][0]["properties"]["subbasin"];
                            var details_html;
                            if (location == "/apps/glass/compare/"){
                                details_html = "/apps/glass/details2/?comid2=" + comid + "&watershed2=" + watershed + "&subbasin2=" + subbasin+"&service=SFPT";
                            }else{
                                details_html = "/apps/glass/details/?comid=" + comid + "&watershed=" + watershed + "&subbasin=" + subbasin+"&service=SFPT";
                            }

                            $(element).popover({
                                'placement': 'top',
                                'html': true,
                                'content': '<table border="1"><tbody><tr><th>Watershed</th><th>Subbasin</th><th>Details</th></tr>' + '<tr><td>' + watershed + '</td><td>' + subbasin + '</td><td><button type="button" class="mod_link btn-primary" data-html="' + details_html + '" >Stream Details</button></td></tr>'
                            });

                            $(element).popover('show');
                            $(element).next().css('cursor', 'text');
                            $('.mod_link').on('click', function () {
                                var details_url = $(this).data('html');
                                window.open(details_url, "_blank");

                            });
                        }
                    });
                }
                if (dr) {
                    $.ajax({
                        type: "GET",
                        url: dr,
                        dataType: 'json',
                        success: function (result) {
                            var site_name = result["features"][0]["properties"]["sitename"];
                            var site_code = result["features"][0]["properties"]["sitecode"];
                            var network = result["features"][0]["properties"]["network"];
                            var hs_url = result["features"][0]["properties"]["url"];
                            var service = result["features"][0]["properties"]["service"];
                            var details_html;
                            if (location == "/apps/glass/compare/"){
                                details_html = "/apps/glass/details2/?sitename=" + site_name + "&sitecode=" + site_code + "&network=" + network + "&hsurl=" + hs_url + "&service=" + service + "&hidenav=true";
                            }else{
                                details_html = "/apps/servir/details/?sitename=" + site_name + "&sitecode=" + site_code + "&network=" + network + "&hsurl=" + hs_url + "&service=" + service + "&hidenav=true";
                            }

                            $(element).popover({
                                'placement': 'top',
                                'html': true,
                                // 'content': '<b>Name:</b>'+site_name+'<br><b>Code:</b>'+site_code+'<br><button type="button" class="mod_link btn-primary" data-html="'+details_html+'" >Site Details</button>'
                                'content': '<table border="1"><tbody><tr><th>Site Name</th><th>Site Id</th><th>Details</th></tr>' + '<tr><td>' + site_name + '</td><td>' + site_code + '</td><td><button type="button" class="mod_link btn-primary" data-html="' + details_html + '" >Site Details</button></td></tr>'
                            });

                            $(element).popover('show');
                            $(element).next().css('cursor', 'text');
                            $('.mod_link').on('click', function () {
                                var details_url = $(this).data('html');
                                window.open(details_url, "_blank");
                            });
                        }
                    });
                }

            }
        });

        map.on('pointermove', function(evt) {
            if (evt.dragging) {
                return;
            }
            var pixel = map.getEventPixel(evt.originalEvent);
            var hit = map.forEachLayerAtPixel(pixel, function(layer) {
                if (layer != layers[0]  ){
                    return true;}
            });
            map.getTargetElement().style.cursor = hit ? 'pointer' : '';
        });


    };

    generate_plot = function(){
        var $loading = $('#view-file-loading');
        $loading.removeClass('hidden');
        $("#plotter").addClass('hidden');
        $SoapVariable = $('#soap_variable');
        var datastring = $SoapVariable.serialize();
        $.ajax({
            type: "POST",
            url: '/apps/glass/soap-api/',
            dataType: 'JSON',
            data: datastring,
            success: function(result){

                $('#plotter').highcharts({
                    chart: {
                        type:'area',
                        zoomType: 'x'
                    },
                    title: {
                        text: result['soap']['title'],
                        style: {
                            fontSize: '11px'
                        }
                    },
                    xAxis: {
                        type: 'datetime',
                        labels: {
                            format: '{value:%d %b %Y}',
                            rotation: 45,
                            align: 'left'
                        },
                        title: {
                            text: 'Date'
                        }
                    },
                    yAxis: {
                        title: {
                            text: result['soap']['unit']
                        }

                    },
                    exporting: {
                        enabled: true
                    },
                    series: [{
                        data: result['soap']['values'],
                        name: result['soap']['variable']
                    }]

                });
                $("#plotter").removeClass('hidden');
                $loading.addClass('hidden');

            },
            error: function(XMLHttpRequest, textStatus, errorThrown)
            {
                $(document).find('.warning').html('<b>Unable to generate graph. Please check the start and end dates and try again.</b>');
                console.log(Error);
            }
        });
        return false;

    };

    $('#generate-plot').on('click',generate_plot);


    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/
    /*
     * Library object that contains public facing functions of the package.
     * This is the object that is returned by the library wrapper function.
     * See below.
     * NOTE: The functions in the public interface have access to the private
     * functions of the library because of JavaScript function scope.
     */
    public_interface = {

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        // Initialize Global Variables

        init_map();

    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.