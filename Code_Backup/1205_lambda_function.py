#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 13:31:38 2019

@author: eva
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import logging
import requests
import ask_sdk_core.utils as ask_utils
import os
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import DialogState
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
from ask_sdk_model import ui

from ask_sdk_model import Response

from Address import get_device_address
from get_reviews import review_sentiment_mean

import threading

import VenueDic as vd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#import WhichBeerIntentHandler


##############################
# Messages
##############################

error = "Sorry, there was a problem."
session_end = "Thank you for using NearBeer. See you soon!"
help_message = "Ask NearBeer for the closest place to get a beer or how much you already drank."



##############################
# Fake Data
##############################

list_of_bars = ["Atzinger", "Der Kleine Kranich", "Fox", "Rennbahn Schwabing"]
list_of_beers = [{"name":"Augustiner Lagerbier Hell", "alcohol":5.2}, {"name":"Paulaner Münchner Hell", "alcohol":4.9}]


alcohol_counter = []
##############################
# On Launch
##############################


class LaunchRequestHandler(AbstractRequestHandler):
    # Handler for Skill Launch
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        
        
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("name" in attr and "gender" in attr and "weight" in attr)
        
        if attributes_are_present:
            speak_output = "Welcome back {name}. Should i search for bars near you, which will take a few seconds?".format(name=attr["name"])

        else:
            speak_output = "To add a user profile, please say add user profile."
        
                
        return(handler_input.response_builder
        .speak(speak_output)
        .ask(speak_output)
        .response
        )


##############################
# User Data
##############################

class UserProfileHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("UserProfile")(handler_input)
    
    def handle(self, handler_input):
        attributes_manager = handler_input.attributes_manager
        slots = handler_input.request_envelope.request.intent.slots
        
        name = slots["name"].value
        gender = slots["gender"].value
        weight = slots["weight"].value
        
        user = {"name":name, "gender":gender, "weight":weight}
        attributes_manager.persistent_attributes = user
        attributes_manager.save_persistent_attributes()
        
        card = ui.StandardCard(
                title="{name}, this is your NearBeer profile".format(name=name),
                text="Name: {name}\nGender: {gender}\nWeight: {weight}kg".format(name=name, gender=gender, weight=weight))
                
        speak_output = " Alright, now we can start with the funny part. If you wan't to drink a specific beer you can ask me where you can get it, else you can ask me which beer you should drink."
        
        return(handler_input.response_builder
            .set_card(card)
            .speak(speak_output)
            .ask(speak_output)
            .response
            )


class DeleteUserIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DeleteUserIntent")(handler_input)
        
        
    def handle(self, handler_input):
        attributes_manager = handler_input.attributes_manager
        attributes_manager.delete_persistent_attributes()
        
        speak_output = "I deleted the persistent attributes."
        
        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
            )

##############################
# Create Venue Dictionary
##############################


class YesHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.info("Test if can handle yes intent, Ergebnis:")
        logger.info(""+str(ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)))
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("Handle yes Intent handler")
        return SearchBarIntentHandler().handle(handler_input)


class NoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        if(len(vd.getVenueInfoDic()) == 0):
            speak_output = "Ok without bars near you, you don't have all options. If you change your mind please ask me to search for bars. What do you want to do now?"
        else:
            speak_output = "Ok, you can always ask me to search for bars again. What do you want do do next?"
        
        return (handler_input.response_builder
        .speak(speak_output)
        .ask(speak_output)
        .response
        )

    
class SearchBarIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SearchBarIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("Search for bar intent handler")
        venue_info_dic = vd.createVenueInfoDic()
        logger.info("venue_info_dic ready")

        if(type(venue_info_dic) == str):
            speak_output = venue_info_dic
        elif(len(venue_info_dic) < 20 ):
            speak_output = "I found {} bars near you. Should i search for more?".format(len(vd.getVenueInfoDic()))
        else:
            speak_output = "Ok I got all bars. What do you want to do next?"
        
        return (handler_input.response_builder
        .speak(speak_output)
        .set_should_end_session(False)
        .response
        )


##############################
# Beer
##############################

class WhichBeerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WhichBeerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "<say-as interpret-as='interjection'>Try a helles!</say-as>"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class ClosestBeerIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ClosestBeerIntent")(handler_input)

    def handle(self, handler_input):

        venue_info_dic = vd.getVenueInfoDic()
        logger.info("venue_info_dic" + str(venue_info_dic))

        slots = handler_input.request_envelope.request.intent.slots
        beer = slots["beer_name"].value

        if(type(venue_info_dic) == str):
            speak_output = venue_info_dic
        elif len(venue_info_dic) == 0:
            speak_output = "Sorry, I cant find a bar with the beer because i didn't search for bars. If you want to search know ask me to do so."
        else:
            result = vd.getBeerFromNearestVenueDic(beer)
            logger.info("get beer result: "+ str(result))
            if(type(result) == str):
                logger.info("neares venue returned string")
                speak_output = result
            else:
                beer, venue = result
                venue_info_dic = vd.getVenueInfoDic()
                logger.info("Found "+beer["name"]+"at "+venue+" location: "+venue_info_dic[venue]["address"])
                speak_output = "The closest place to drink a {beer} is {bar}! The address is {address}.".format(beer=beer["name"], bar=venue, address=venue_info_dic[venue]["address"])
                card = ui.StandardCard(
                    title="I found something",
                    text="The closest place to drink a {beer} is {bar}! The address is {address}.".format(beer=beer["name"], bar=venue, address=venue_info_dic[venue]["address"]),
                    image = ui.Image(
                        # hier wird dann das Bild des jeweiligen Biers eingefügt
                        small_image_url="https://www.augustiner-nuernberg.de/wp-content/uploads/2017/12/augustiner-nuernberg-Lagerbier-Hell.jpg")
                    )
                
        return (
            handler_input.response_builder
                .set_card(card)
                .speak(speak_output)
                .set_should_end_session(False)
                .response
        )


class AddBeerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AddBeerIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        dialog_state = handler_input.request_envelope.request.dialog_state
        
        if dialog_state == "STARTED":
            return (handler_input.response_builder
            .speak("First, please tell me the name of the brewery")
            .set_should_end_session(False)
            .response
            )
        
        slots = handler_input.request_envelope.request.intent.slots
        beer = slots["beer"].value
        amount = slots["amount"].value
        brewery = slots["brewery"].value
        
        if amount == "pint" or amount == "zero point five" or amount == "bottle":
            amount = 0.5
        elif amount == "zero point three":
            amount = 0.3
        elif amount == "zero point two":
            amount = 0.2
        
        beer_api = beer.replace(" ", "+")
        brewery_api = brewery.replace(" ", "+")
        url = "https://data.opendatasoft.com/api/records/1.0/search//?dataset=open-beer-database%40public-us&q=name:" + beer_api + "+and+name_breweries:" + brewery_api + "&refine.country=Germany"
        response = requests.get(url)
        
        if response.status_code == 200:
            abv = 0
            response = response.json()
            
            if len(response["records"]) == 1:
                abv = response["records"][0]["fields"]["abv"]
                if abv != 0:
                    volume = (abv/100)*amount
                    amount = str(amount)
                    alcohol_counter.append(volume)
                    speak_output = "I added {0} liters of {1} to your alcohol counter. Your alcohol level is now {2:.2f}.".format(amount, beer, volume)
                    
                else:
                    speak_output = "Unfortunately, I can't find the alcohol by volume level of" + beer +". Do you want to add this information?"
                    
            elif len(response["records"]) == 0:
                speak_output = "There was no beer found."
            
            else:
                speak_output = "I found several beers matching your input. Please change your input"
                        
        else:
            speak_output = "I had trouble getting the alcohol by volume of " + beer + "."
                
        return (handler_input.response_builder
            .speak(speak_output)
            .set_should_end_session(False)
            .response
            )



##############################
# Calculating BAC Calculator
##############################

"""  BAC = [Alcohol consumed in grams / (Body weight in grams x r)] x 100"""
"""  “r” is the gender constant: r = 0.55 for females and 0.68 for males."""

class BACCalculatorIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BACIntent")(handler_input)
    
    def handle(self, handler_input):
        attributes_manager = handler_input.attributes_manager
        
        persistent_attributes = attributes_manager.persistent_attributes
        weight = int(persistent_attributes["weight"])
        gender = persistent_attributes["gender"]
        
        alcoholAmount = sum(alcohol_counter)
        
        
        if gender == "male":
            r = 0.68
        elif gender == "female":
            r = 0.55
        else: 
            r = 0.6
        
        bac = alcoholAmount / (weight * r) * 100
        
        if bac <= 0.5:
            speak_output = "Your BAC is {0:.2f}. You can stil drive, but be careful.".format(bac)
        else:
            speak_output = "Your BAC is {0:.2f}. This is too much for driving.".format(bac)
        
        
        
        return (handler_input.response_builder
            .speak(speak_output)
            .response
            )


##############################
# Bar Review
##############################

class BarReviewIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BarReviewIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        bar_name = handler_input.request_envelope.request.intent.slots["barname"].value
        mean_review = review_sentiment_mean(bar_name)
        
        if mean_review <= 0.3:
            speak_output = "<amazon:emotion name='disappointed' intensity='high'>The reviews of that bar are not very good. You should go somewhere else.</amazon:emotion>"
        elif mean_review <= 0.6:
            speak_output = "The reviews of that bar are okay, but there are better bars around."
        else:
            speak_output = "<amazon:emotion name='excited' intensity='high'>The reviews of that bar are great, you should definitely go there.</amazon:emotion>"
        #speak_output = "The mean review is {}".format(mean_review)
        return (handler_input.response_builder
            .speak(speak_output)
            .set_should_end_session(False)
            .response
            )



##############################
# Route to bar
##############################

class RouteToBarIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RouteToBarIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        card = ui.StandardCard(
                title="Route to Bar",
                text="link")
            
        speak_output = "Click on the card to navigate to the bar."
        
        return (handler_input.response_builder
            .set_card(card)
            .speak(speak_output)
            .set_should_end_session(False)
            .response
            )


##############################
# Required Intents
##############################

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = help_message

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = session_end

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

sb = CustomSkillBuilder(persistence_adapter=s3_adapter, api_client=DefaultApiClient())

####### On Launch #########
sb.add_request_handler(LaunchRequestHandler())

####### Search Bars #######
sb.add_request_handler(SearchBarIntentHandler())
sb.add_request_handler(YesHandler())
sb.add_request_handler(NoHandler())

####### User Data #########
sb.add_request_handler(UserProfileHandler())
sb.add_request_handler(DeleteUserIntentHandler())

####### Beer #########
sb.add_request_handler(WhichBeerIntentHandler())
sb.add_request_handler(ClosestBeerIntentHandler())
sb.add_request_handler(AddBeerIntentHandler())

####### Bar Review #######
sb.add_request_handler(BarReviewIntentHandler())

####### Route to bar #######
sb.add_request_handler(RouteToBarIntentHandler())

####### BACCalculation #########
sb.add_request_handler(BACCalculatorIntentHandler())

####### Required Intents #########
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
