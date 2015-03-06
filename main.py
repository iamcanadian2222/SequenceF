#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import time

# import some appengine libraries to make it easier to store data / login
from google.appengine.api import users
from google.appengine.ext import ndb


# setup our models
def get_sessions_key():
    """Constructs a Datastore key for the sessions entity."""
    return ndb.Key('Sessions', "sessions")


class ModelUtils(object):
    def to_dict(self):
        result = super(ModelUtils,self).to_dict()
        result['key'] = self.key.id()  # get the key as a string
        return result


class Session(ModelUtils, ndb.Model):
    """A main model for representing an individual Session entry."""
    # session_id = ndb.StringProperty()
    name = ndb.StringProperty()
    sequence = ndb.IntegerProperty(repeated=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


def date_handler(obj):
    return time.mktime(obj.timetuple()) if hasattr(obj, 'isoformat') else obj
    # return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def get_sessions(self):
    sessions_query = Session.query(ancestor=get_sessions_key()).order(-Session.date)
    return sessions_query.fetch()  # get everything as a test


def get_session(session_id):
    """Given a session_id, return the Session object"""
    return Session.get_by_id(int(session_id),parent=get_sessions_key())


def add_session(sequence, name):
    session = Session(parent=get_sessions_key())  # to store a custom key_name in ndb, use id=XXX
    # session.session_id = session_id
    session.sequence = sequence
    session.name = name
    key = session.put()
    return key.id()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        f = open("static/index.html")
        self.response.write(f.read())
        # self.response.write("Welcome to the sequence mutilator!<br />"
        #                     "<a href='/add'>Add Sequence</a>")
        # self.response.write(" &#8226; <a href='/admin'>Admin</a>")  # only allow this for admins (later)


class SessionHandler(webapp2.RequestHandler):
    def get(self):
        sessions = get_sessions(self)
        self.response.write(json.dumps([session.to_dict() for session in sessions], default=date_handler))

    # create a new session (with a new sequence array in the body
    def post(self):
        json_string = self.request.body
        json_object = json.loads(json_string)
        sequence = json_object["sequence"]
        name = json_object["name"]
        if sequence is not None and name is not None:
            # session_id = generate_session_id()
            session_key = add_session(sequence, name)

            # json_response = {"session_id": str(session_key), "sequence": sequence}
            self.response.write(json.dumps(get_session(session_key).to_dict(), default=date_handler))


class SequenceHandler(webapp2.RequestHandler):
    def get(self, session_id):
        session = get_session(session_id)
        self.response.write(json.dumps(session.to_dict(), default=date_handler))

    def delete(self, session_id):
        session = get_session(session_id)
        session.key.delete()

    def put(self, session_id):
        json_object = json.loads(self.request.body)
        session_id2 = json_object["session_key"]
        sequence = json_object["sequence"]
        name = json_object["name"]
        if long(session_id2) != long(session_id) or sequence is None:  # make sure the session_id used in the URL matches the body
            self.response.set_status(400)
        else:
            session = get_session(session_id)
            session.name = name  # emptying out the name is legal in our implementation
            session.sequence = sequence
            session.put()



valid_methods = ["next-largest", "next-smallest", "largest", "smallest"]
class MethodHandler(webapp2.RequestHandler):
    def get(self, session_id, method, parameter=None):
        if method not in valid_methods:
            self.response.set_status(400)
        else:
            response = {}
            json_object = json.loads(self.request.body) if self.request.body is not "" else None
            if method == "next-largest":
                if parameter is not None:
                    response["next_largest_index"] = get_next_largest(session_id, parameter)
            self.response.write(json.dumps(response))





def get_next_largest(session_id, index):
    index = int(index)
    sequence = get_session(session_id).sequence
    if len(sequence) <= 1 or index < 0 or index > len(sequence):
        return -1
    index_value = sequence[index]
    for n in range(index, len(sequence)):
        if sequence[n] > index_value:
            return n
    return -1  # if we get this far, we didn't find a larger value


# --- POST /session/ { "sequence": [ 1, 2, 3, 4, 1] }
# --- GET /session/:sessionid/nextHighestIndex/:index
# --- GET /session/:id/
# DELETE /session/:id

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    webapp2.Route("/sequence", handler=SessionHandler),  # originally filtered to just POSTs: , methods=["POST"]
    webapp2.Route("/sequence/<session_id>", handler=SequenceHandler, methods=["GET", "DELETE", "PUT"]),
    webapp2.Route("/sequence/<session_id>/<method>", handler=MethodHandler),
    webapp2.Route("/sequence/<session_id>/<method>/<parameter:\w+>", handler=MethodHandler),
], debug=True)
