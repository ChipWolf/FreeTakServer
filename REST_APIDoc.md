# FreeTAKServer REST API Documentation
the FreeTAKServer REST API is a human readeble approach to the TAK world. the API  allows you to connect easily third parties to the TAK family, without the need to understand the complexity of the COT structure or what a TCP connection is.  

In the current release FTS supports following API:
  * SendGeoEvent
  * SendGeoChatToAll
  * Send Emergency
  
## Authorization
the authorization is placed in the header of the message.
Authorization: [YOUR_API_KEY]

you need to request the key to the FTS admin. the following is a non working example
```
{“Authorization”: “K0rv0 meg@secre7apip@guesmeIfyouCan”}
```


## API List
  ### SendGeoObject
  
 a GeoObject is an element place on a map. It has a name, characteristics and an attitude. 

  * GeoObject: It's the information that will determine which type will be placed on the tak maps including his icon. Please see API documentation for a list of valid entries.
  *  longitude: the angular distance of the geoobject from the meridian of the greenwich, UK expressed in positive or negative float. (e.g -76.107.7998).  remember to set the display of your TAK in decimal cohordinates, where *West 77.08* is equal to '-77.08' in the API
  * latitude: the angular distance of the geoobject from the earths equator expressed in positive or negative float. (e.g 43.855682)
  * How: the way in which this geo information has been acquired. Please see API documentation for a list of valid entries.
  * attitude: the kind of expected behavior of the GeoObject (e.g friendly, hostile, unknown). Please see API documentation for a list of valid entries.


  
  #### Example body
```
{
"longitude": -77.0104,
"latitude": 38.889,
"attitude": "hostile",
"geoObject": "Gnd Combat Infantry Sniper",
"how": "nonCoT",
"name": "Putin"
}
```
  
 ### List of supported Geo Objects
  * "Gnd Combat Infantry Rifleman"
  * "Gnd Combat Infantry grenadier" 
  * "Gnd Combat Infantry Mortar" 
  * "Gnd Combat Infantry MachineGunner (LMG)" 
  * "Gnd Combat Infantry Medic" 
  * "Gnd Combat Infantry Sniper"
  * "Gnd Combat Infantry Recon" 
  * "Gnd Combat Infantry anti Tank" 
  * "Gnd Combat Infantry air defense"
  * "Gnd Combat Infantry Engineer" 
