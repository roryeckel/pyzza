import requests
from datetime import datetime
from bs4 import BeautifulSoup
from threading import Timer

class Tracker:
    """The base pizza tracker class that retrieves and contains data"""

    def _strptime(time, time_format='%Y-%m-%dT%H:%M:%S'):
        """Format the time returned by the Dominos api"""
        if time is not None and time:
            return datetime.strptime(time, time_format)
        return None
    
    def __init__(self, store_id, order_key, do_update=True):
        """Initialize a Tracker with a store ID and order key, then update()"""
        self.store_id = store_id
        self.order_key = order_key
        if do_update:
            self.update()

    def update(self):
        """Retrieve order status"""
        response = requests.get('https://order.dominos.com/'
                                'orderstorage/GetTrackerData?'
                                'StoreID={store_id}&OrderKey={order_key}'.format(
                                    store_id=self.store_id,
                                    order_key=self.order_key)).text
        self.last_update = datetime.now()
        xml = BeautifulSoup(response, 'html.parser')
        self.version = xml.find('version').get_text()
        self.order_id = xml.find('orderid').get_text()
        self.phone = xml.find('phone').get_text()
        self.service_method = xml.find('servicemethod').get_text()
        self.orders = [x.strip() for x in xml.find('orderdescription').get_text().split('\n') if x]
        self.driver_name = xml.find('drivername').get_text()
        self.manager_name = xml.find('managername').get_text()
        self.driver_id = xml.find('driverid').get_text()
        self.as_of = Tracker._strptime(xml.find('asof').get_text())
        self.status = xml.find_all('orderstatus')[1].get_text()
        self.start_time = Tracker._strptime(xml.find('starttime').get_text())
        self.oven_time = Tracker._strptime(xml.find('oventime').get_text())
        self.rack_time = Tracker._strptime(xml.find('racktime').get_text())
        self.route_time = Tracker._strptime(xml.find('routetime').get_text())
        self.delivery_time = Tracker._strptime(xml.find('deliverytime').get_text())

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return ('Phone #: {phone}, Order ID: {order_id}, Store ID: {store_id}, Order Key: {order_key}\n'\
                'Driver Name: {driver_name}, Manager Name: {manager_name}\n\n'\
                'Started {start_time} | Put in oven at {oven_time} | Rack: {rack_time} | '\
                'Delivery started at {route_time} | Delivered {delivery_time}\n'\
                'Update Time: {as_of}').format(**self.__dict__)

class AutoTracker:
    """An automatic Tracker updater"""

    def update(self):
        """Update the contained tracker object and schedule another update"""
        if hasattr(self, 'timer') and self.timer is not None:
            self.timer.cancel()
        self.tracker.update()
        self.callback(self)
        self.timer = Timer(self.interval, self.update)
        self.timer.start()

    def __init__(self, tracker, callback=None, interval=10):
        """Initialize an AutoTracker with Tracker object and an interval, default 10 seconds"""
        self.tracker = tracker
        self.callback = callback
        self.interval = interval
        self.update()

    def on_update(self, callback):
        """Set a callback to execute when updated"""
        self.callback = callback

def print_update(auto_tracker):
    print()
    print(auto_tracker.tracker)
    print()
