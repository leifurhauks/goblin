"""Simply custom geometry classes that correpond to Titan:db geoshapes"""
from geojson import geometry


class Circle(geometry.Geometry):

    def __init__(self, coordinates):
        super(Circle, self).__init__(coordinates=coordinates)
        self.lng = coordinates[0]
        self.lat = coordinates[1]
        self.radius = coordinates[2]

    @property
    def __geo_interface__(self):
        return {'type': 'circle',
                'coordinates': [
                    [(self.x, self.y, self.radius)]
                ]}
