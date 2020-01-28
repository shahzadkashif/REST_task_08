from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from .models import Flight, Booking, Profile


class FlightListTest(APITestCase):
	def setUp(self):
		self.flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		self.flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}
		Flight.objects.create(**self.flight1)
		Flight.objects.create(**self.flight2)

	def test_url_works(self):
		response = self.client.get(reverse('flights-list'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_list(self):
		response = self.client.get(reverse('flights-list'))
		flights = Flight.objects.all()
		self.assertEqual(len(response.data), flights.count())
		flight = flights[0]
		self.assertEqual(dict(response.data[0]), {"id" : flight.id, "destination" : flight.destination, "time": str(flight.time), "price": str(flight.price)})
		flight = flights[1]
		self.assertEqual(dict(response.data[1]), {"id" : flight.id, "destination" : flight.destination, "time": str(flight.time), "price": str(flight.price)})


class BookingListTest(APITestCase):
	def setUp(self):
		self.flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		self.flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}
		flight1 = Flight.objects.create(**self.flight1)
		flight2 = Flight.objects.create(**self.flight2)
		user1 = User(username="laila")
		user1.set_password("1234567890-=")
		user1.save()
		user2 = User(username="laila2")
		user2.set_password("1234567890-=")
		user2.save()

		Booking.objects.create(flight=flight1, date="2020-01-01", user=user1, passengers=2)
		Booking.objects.create(flight=flight2, date="2019-01-01", user=user1, passengers=2)
		Booking.objects.create(flight=flight1, date="2031-01-01", user=user2, passengers=2)
		Booking.objects.create(flight=flight2, date="2031-01-01", user=user2, passengers=2)

		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])


	def test_url_works(self):
		response = self.client.get(reverse('bookings-list'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_url_unauthorized(self):
		self.client.credentials()
		response = self.client.get(reverse('bookings-list'))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_response(self):
		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.get(reverse('bookings-list'))

		user = User.objects.get(username="laila")
		bookings = Booking.objects.filter(user=user, date__gt=date.today())
		self.assertEqual(len(response.data), bookings.count())

		for index, booking in enumerate(bookings):
			self.assertEqual(dict(response.data[index]), {"id" : booking.id, "flight" : booking.flight.destination, "date": str(booking.date)})



class BookingDetails(APITestCase):
	def setUp(self):
		flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}

		flight1 = Flight.objects.create(**flight1)
		flight2 = Flight.objects.create(**flight2)

		user1 = User(username="laila")
		user1.set_password("1234567890-=")
		user1.save()
		user2 = User(username="laila2")
		user2.set_password("1234567890-=")
		user2.save()

		Booking.objects.create(flight=flight1, date="2018-01-01", user=user1, passengers=2)
		Booking.objects.create(flight=flight2, date="2019-01-01", user=user1, passengers=2)
		Booking.objects.create(flight=flight1, date="2020-01-01", user=user2, passengers=2)
		Booking.objects.create(flight=flight2, date="2021-01-01", user=user2, passengers=2)

	def test_url_works(self):
		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.get(reverse('booking-details', args=[1]))
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.get(reverse('booking-details', args=[2]))
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_url_forbidden(self):
		response = self.client.post(reverse('login'), {"username" : "laila2", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])		
		response = self.client.get(reverse('booking-details', args=[1]))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])		
		response = self.client.get(reverse('booking-details', args=[3]))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_url_unauthorized(self):
		response = self.client.get(reverse('booking-details', args=[1]))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_response(self):
		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

		response = self.client.get(reverse('booking-details', args=[1]))
		booking = Booking.objects.get(id=1)
		self.assertEqual(dict(response.data), {"id" : booking.id, "flight" : {'destination': booking.flight.destination, 'time': str(booking.flight.time), 'price': str(booking.flight.price), 'id': booking.flight.id}, "total": booking.flight.price*booking.passengers, "date": str(booking.date), "passengers":booking.passengers})

		response = self.client.get(reverse('booking-details', args=[2]))
		booking = Booking.objects.get(id=2)
		self.assertEqual(dict(response.data), {"id" : booking.id, "flight" : {'destination': booking.flight.destination, 'time': str(booking.flight.time), 'price': str(booking.flight.price), 'id': booking.flight.id}, "total": booking.flight.price*booking.passengers, "date": str(booking.date), "passengers":booking.passengers})



class BookingUpdate(APITestCase):
	def setUp(self):
		flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}

		flight1 = Flight.objects.create(**flight1)
		flight2 = Flight.objects.create(**flight2)
		user = User(username="laila")
		user.set_password("1234567890-=")
		user.save()

		user2 = User(username="laila2")
		user2.set_password("1234567890-=")
		user2.save()

		admin = User(username="admin", is_staff=True)
		admin.set_password("1234567890-=")
		admin.save()

		Booking.objects.create(flight=flight1, date=date.today(), user=user, passengers=2)
		Booking.objects.create(flight=flight2, date=date.today()+timedelta(days=2), user=user, passengers=2)
		Booking.objects.create(flight=flight1, date=date.today()+timedelta(days=4), user=user2, passengers=2)
		Booking.objects.create(flight=flight2, date="2021-01-01", user=user, passengers=2)

	def test_url_works(self):
		response = self.client.post(reverse('login'), {"username":"laila", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

		data = {"date": "2019-05-05", "passengers": 4}
		response = self.client.put(reverse('update-booking', args=[4]), data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_url_unauthorized(self):
		data = {"date": "2019-05-05", "passengers": 4}
		response = self.client.put(reverse('update-booking', args=[1]), data)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_url_forbidden(self):
		response = self.client.post(reverse('login'), {"username":"laila", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

		data = {"date": "2019-05-05", "passengers": 4}
		response = self.client.put(reverse('update-booking', args=[1]), data)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		response = self.client.put(reverse('update-booking', args=[2]), data)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		response = self.client.put(reverse('update-booking', args=[3]), data)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_update_admin(self):
		data = {"date": "2019-05-05", "passengers": 4}

		response = self.client.post(reverse('login'), {"username":"admin", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

		old_booking = Booking.objects.get(id=4)
		response = self.client.put(reverse('update-booking', args=[4]), data)
		new_booking = Booking.objects.get(id=4)
		self.assertEqual({"id":old_booking.id, "date":data["date"], "passengers":data["passengers"], "flight":old_booking.flight, "user":old_booking.user}, {"id":new_booking.id, "date":str(new_booking.date), "passengers":new_booking.passengers, "flight":new_booking.flight, "user":new_booking.user})

		old_booking = Booking.objects.get(id=3)
		response = self.client.put(reverse('update-booking', args=[3]), data)
		new_booking = Booking.objects.get(id=3)
		self.assertEqual({"id":old_booking.id, "date":data["date"], "passengers":data["passengers"], "flight":old_booking.flight, "user":old_booking.user}, {"id":new_booking.id, "date":str(new_booking.date), "passengers":new_booking.passengers, "flight":new_booking.flight, "user":new_booking.user})

	def test_update_normal(self):
		data = {"date": "2019-05-05", "passengers": 4}

		response = self.client.post(reverse('login'), {"username":"laila", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

		old_booking = Booking.objects.get(id=4)
		response = self.client.put(reverse('update-booking', args=[4]), data)
		new_booking = Booking.objects.get(id=4)
		self.assertEqual({"id":old_booking.id, "date":str(old_booking.date), "passengers":data["passengers"], "flight":old_booking.flight, "user":old_booking.user}, {"id":new_booking.id, "date":str(new_booking.date), "passengers":new_booking.passengers, "flight":new_booking.flight, "user":new_booking.user})


class BookingDelete(APITestCase):
	def setUp(self):
		flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}

		flight1 = Flight.objects.create(**flight1)
		flight2 = Flight.objects.create(**flight2)

		user = User(username="laila")
		user.set_password("1234567890-=")
		user.save()

		user2 = User(username="laila2")
		user2.set_password("1234567890-=")
		user2.save()

		admin = User(username="admin", is_staff=True)
		admin.set_password("1234567890-=")
		admin.save()

		Booking.objects.create(flight=flight1, date=date.today(), user=user, passengers=2)
		Booking.objects.create(flight=flight2, date=date.today()+timedelta(days=2), user=user, passengers=2)
		Booking.objects.create(flight=flight1, date=date.today()+timedelta(days=4), user=user2, passengers=2)
		Booking.objects.create(flight=flight2, date="2021-01-01", user=user, passengers=2)

	def test_url_works(self):
		response = self.client.post(reverse('login'), {"username":"laila", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.delete(reverse('cancel-booking', args=[4]))
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

	def test_url_unauthorized(self):
		response = self.client.delete(reverse('cancel-booking', args=[4]))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_url_forbidden(self):
		response = self.client.post(reverse('login'), {"username":"laila", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.delete(reverse('cancel-booking', args=[1]))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		response = self.client.delete(reverse('cancel-booking', args=[2]))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		response = self.client.delete(reverse('cancel-booking', args=[3]))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_delete_normal(self):
		response = self.client.post(reverse('login'), {"username":"laila", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.delete(reverse('cancel-booking', args=[4]))
		self.assertEqual(Booking.objects.all().count(), 3)
		self.assertEqual(Booking.objects.filter(id=4).count(), 0)

	def test_delete_admin(self):
		response = self.client.post(reverse('login'), {"username":"admin", "password":"1234567890-="})
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.delete(reverse('cancel-booking', args=[4]))
		self.assertEqual(Booking.objects.all().count(), 3)
		self.assertEqual(Booking.objects.filter(id=4).count(), 0)

		response = self.client.delete(reverse('cancel-booking', args=[3]))
		self.assertEqual(Booking.objects.all().count(), 2)
		self.assertEqual(Booking.objects.filter(id=3).count(), 0)


class Login(APITestCase):
	def setUp(self):
		flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}

		flight1 = Flight.objects.create(**flight1)
		flight2 = Flight.objects.create(**flight2)

		self.data = {"username":"laila", "password":"1234567890-="}
		user = User(username=self.data["username"])
		user.set_password(self.data["password"])
		user.save()

	def test_succeful_login(self):
		response = self.client.post(reverse('login'), self.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_unsucceful_login(self):
		response = self.client.post(reverse('login'), {"username" : "laila", "password": "1234567890-=1"})
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookingCreate(APITestCase):
	def setUp(self):
		self.user_data = {"username":"laila", "password":"1234567890-="}
		self.data = {"date": "2019-05-05", "passengers": 4}
		user = User(username=self.user_data["username"])
		user.set_password(self.user_data["password"])
		user.save()

		user = User(username=self.user_data["username"]+"1")
		user.set_password(self.user_data["password"])
		user.save()

		flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}
		self.flight1 = Flight.objects.create(**flight1)
		self.flight2 = Flight.objects.create(**flight2)


	def test_url_works(self):
		response = self.client.post(reverse('login'), self.user_data)
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.post(reverse('book-flight', args=[1]), self.data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_url_unauthorized(self):
		response = self.client.post(reverse('book-flight', args=[1]), self.data)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		

	def test_creation_works(self):
		response = self.client.post(reverse('login'), self.user_data)
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

		user = User.objects.get(id=1)

		response = self.client.post(reverse('book-flight', args=[1]), self.data)
		bookings = Booking.objects.all()
		self.assertEqual(bookings.count(), 1)
		self.assertEqual(bookings[0].user, user)
		self.assertEqual(bookings[0].flight, self.flight1)
		self.assertEqual(bookings[0].passengers, self.data["passengers"])
		self.assertEqual(str(bookings[0].date), self.data["date"])

		user = User.objects.get(id=1)

		response = self.client.post(reverse('book-flight', args=[2]), self.data)
		bookings = Booking.objects.all()
		self.assertEqual(bookings.count(), 2)
		self.assertEqual(bookings[1].user, user)
		self.assertEqual(bookings[1].flight, self.flight2)
		self.assertEqual(bookings[1].passengers, self.data["passengers"])
		self.assertEqual(str(bookings[1].date), self.data["date"])


class Register(APITestCase):
	def test_url_works(self):
		data = {"username": "laila", "password": "1234567890-=", "first_name": "laila", "last_name":  "bee"}
		response = self.client.post(reverse('register'), data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_user(self):
		data = {"username": "laila", "password": "1234567890-=", "first_name": "laila", "last_name":  "bee"}
		response = self.client.post(reverse('register'), data)
		users = User.objects.all()
		self.assertEqual(users.count(), 1)

		data["username"] = "laila2"
		response = self.client.post(reverse('register'), data)
		users = User.objects.all()
		self.assertEqual(users.count(), 2)

	def test_correct_creation(self):
		data = {"username": "laila", "password": "1234567890-=", "first_name": "laila", "last_name":  "bee"}
		response = self.client.post(reverse('register'), data)
		user = User.objects.get(id=1)

		self.assertEqual(data["first_name"], user.first_name)
		self.assertEqual(data["last_name"], user.last_name)
		self.assertEqual(data["username"], user.username)

		response = self.client.post(reverse('login'), {"username" : data["username"], "password":data["password"]})
		self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileDetails(APITestCase):
	def setUp(self):
		flight1 = {'destination': 'Wakanda', 'time': '10:00', 'price': 230, 'miles': 4000}
		flight2 = {'destination': 'La la land', 'time': '00:00', 'price': 1010, 'miles': 1010}

		flight1 = Flight.objects.create(**flight1)
		flight2 = Flight.objects.create(**flight2)

		self.user_data = {"username" : "laila", "password" : "1234567890-="}

		self.user = User(username=self.user_data["username"])
		self.user.set_password(self.user_data["password"])
		self.user.save()

		Profile.objects.create(user=self.user)

		user2 = User(username="laila2")
		user2.set_password("1234567890-=")
		user2.save()

		Booking.objects.create(flight=flight1, date=date.today(), user=self.user, passengers=2)
		Booking.objects.create(flight=flight2, date=date.today()+timedelta(days=2), user=self.user, passengers=2)
		Booking.objects.create(flight=flight1, date=date.today()+timedelta(days=4), user=user2, passengers=2)
		Booking.objects.create(flight=flight2, date="2021-01-01", user=self.user, passengers=2)

	def test_url_works(self):
		response = self.client.post(reverse('login'), self.user_data)
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.get(reverse("profile-details"))
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_url_unauthorized(self):
		response = self.client.get(reverse("profile-details"))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_serializer(self):
		response = self.client.post(reverse('login'), self.user_data)
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
		response = self.client.get(reverse("profile-details"))

		self.assertEqual(response.data['user'], {"first_name": self.user.first_name, "last_name": self.user.last_name})
		past_bookings = Booking.objects.filter(user=self.user, date__lt=date.today())
		past_bookings_list = []
		for booking in past_bookings:
			past_bookings_list.append({'flight':booking.flight.destination, 'date':str(booking.date), 'id':booking.id})
		self.assertEqual(response.data['past_bookings'], past_bookings_list)
		self.assertEqual(response.data['miles'], self.user.profile.miles)
		miles = self.user.profile.miles
		if miles < 10000:
			tier =  "Blue"
		elif miles < 60000:
			tier =  "Silver"
		elif miles < 100000:
			tier =  "Gold"
		else:
			tier =  "Platinum"

		self.assertEqual(response.data['tier'], tier) 



