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
    return ndb.Key()
    # session_query = Session.query(Session.key == session_id, ancestor=get_sessions_key())
    #return session_query.fetch()


def add_session(sequence):
    session = Session(parent=get_sessions_key())  # to store a custom key_name in ndb, use id=XXX
    # session.session_id = session_id
    session.sequence = sequence
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
        if sequence is not None:
            # session_id = generate_session_id()
            session_key = add_session(sequence)

            # json_response = {"session_id": str(session_key), "sequence": sequence}
            self.response.write(json.dumps(get_session(session_key).to_dict(), default=date_handler))

class GetSequenceHandler(webapp2.RequestHandler):
    def get(self, session_id):
        session = get_session(session_id)
        self.response.write(json.dumps(session.to_dict(), default=date_handler))

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


# POST /session/ { "sequence": [ 1, 2, 3, 4, 1] }
# GET /session/:sessionid/nextHighestIndex/:index
# GET /session/:id/currentValues
# DELETE /session/:id

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    webapp2.Route("/sequence", handler=SessionHandler),  # originally filtered to just POSTs: , methods=["POST"]
    webapp2.Route("/sequence/<session_id>", handler=GetSequenceHandler, methods=["GET"]),
    webapp2.Route("/sequence/<session_id>/<method>", handler=MethodHandler),
    webapp2.Route("/sequence/<session_id>/<method>/<parameter:\w+>", handler=MethodHandler),
], debug=True)
