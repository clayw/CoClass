  function getUrlVars()
  {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
      hash = hashes[i].split('=');
      vars.push(hash[0]);
      vars[hash[0]] = hash[1];
    }
    return vars;
  }
  google.load("maps", "2");

  var markers = new Array();
  function initialize() {
    var map = new GMap2(document.getElementById("map_canvas"));
    map.addControl(new GSmallMapControl()); 
    var geocoder = new GClientGeocoder();
    var squery = getUrlVars()['addr'];
    //geocoder.getLatLng(squery, function(point) { map.setCenter(point, 12); });
    var baseIcon = new GIcon(G_DEFAULT_ICON);
    baseIcon.shadow = "http://www.google.com/mapfiles/shadow50.png";
    baseIcon.iconSize = new GSize(20, 34);
    baseIcon.shadowSize = new GSize(37, 34);
    baseIcon.iconAnchor = new GPoint(9, 34);
    baseIcon.infoWindowAnchor = new GPoint(9, 2); 
    function createMarker(point, letter) {
      // Create a lettered icon for this point using our icon class
      var letteredIcon = new GIcon(baseIcon);
      letteredIcon.image = "http://www.google.com/mapfiles/marker" + letter + ".png";

      // Set up our GMarkerOptions object
      markerOptions = { icon:letteredIcon };
      var marker = new GMarker(point, markerOptions);

      return marker;
    } 
    function getBoundsForMarkers(markers) {
    
    
    var minLat = 180;
    var minLng = 180;
    var maxLat = -180;
    var maxLng = -180;
    
    for (var i=0; i<markers.length; i++) {
    var point = markers[i].getLatLng();
    
    if (minLat>point.lat()) minLat = point.lat();
    if (minLng>point.lng()) minLng = point.lng();
    if (maxLat<point.lat()) maxLat = point.lat();
    if (maxLng<point.lng()) maxLng = point.lng();
    }
    
    return new GLatLngBounds(new GLatLng(minLat,minLng), new GLatLng(maxLat,maxLng));
    } 
    {% for result in search_results.object_list %}
      {% if result.lat and result.lng %}
      var marker = createMarker(new GLatLng({{ result.lat }}, {{ result.lng }}), '{{ result.letter }}');
      GEvent.addListener(marker, "click", function () { location.href='{{ result.get_absolute_url }}'; } );
      map.addOverlay(marker);
      markers.push(marker); 
      {% endif %}
    {% endfor %}
     if (markers.length==0) {
     {% if gcode_lat and gcode_lng %}
       var center_loc = new GLatLng({{ gcode_lat }},{{ gcode_lng }});
       map.setCenter(center_loc, 12-2);
     {% else %}
     {% endif %}
     } else {
     var bounds =getBoundsForMarkers(markers);
     map.setCenter(bounds.getCenter());
     map.setZoom(map.getBoundsZoomLevel(bounds));
     } 
  }
  google.setOnLoadCallback(initialize);
window.onunload = google.maps.unload; 
