# -*- coding: utf-8 -*-

# City Guide: A sample Alexa Skill Lambda function
# This function shows how you can manage data in objects and arrays,
# choose a random recommendation,
# call an external API and speak the result,
# handle YES/NO intents with session attributes,
# and return text data on a card.

import logging
import gettext

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type

from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

from alexa import data, util, ddb

# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cuisine = ""

# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        # logger.info(_("This is an untranslated message"))

        speech = _(data.WELCOME)
        speech += " " + _(data.HELP)
        handler_input.response_builder.speak(speech)
        handler_input.response_builder.ask(_(
            data.GENERIC_REPROMPT))
        return handler_input.response_builder.response


class AboutIntentHandler(AbstractRequestHandler):
    """Handler for about intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AboutIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AboutIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        handler_input.response_builder.speak(_(data.ABOUT))
        return handler_input.response_builder.response


class GetCityIntentHandler(AbstractRequestHandler):
    """Handler for getting city intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetCityIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetCityIntentHandler")

        place = ddb.getLocation()
        if (place == "NOWHERE"):
            speech = "I don't know where you are. "
        else:
            speech = ("You are in {}.").format(place)

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response


class AddCityIntentHandler(AbstractRequestHandler):
    """Handler for adding city intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddCityIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AddCityIntentHandler")
        place = util.get_resolved_value(
            handler_input.request_envelope.request, "city")
        if place is None:
            place = "NOWHERE"
            speech = ("I'm sorry. I don't know where that is.")
        else:
            speech = ("You are in {}. I will record that.").format(place)

        ddb.setLocation(place)

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response

class GetDietaryRequirementsIntentHandler(AbstractRequestHandler):
    """Handler for getting dietary requirements."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetDietaryRequirementsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetDietaryRequirementsIntentHandler")

        person = util.get_resolved_value(
            handler_input.request_envelope.request, "person")
        if person is None:
            person = "your"
        else:
            req = ddb.getDietaryReq(person)
            if len(req) != 0:
                speech = ("{} dietary requirements are {}").format(person, req)
            else:
                speech = ("{} has no dietary requirements that I know of.").format(person)
        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response


class AddDietaryRequirementsIntentHandler(AbstractRequestHandler):
    """Handler for adding dietary requirements."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddDietaryRequirementsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AddDietaryRequirementsIntentHandler")
        person = util.get_resolved_value(
            handler_input.request_envelope.request, "person")
        if person is None:
            person = "your"
        dietary_req = util.get_resolved_value(
            handler_input.request_envelope.request, "dietary_req")
        speech = ("Okay. I'll remember that {} is {}.").format(person, dietary_req)

        ddb.addDietaryReq(person, dietary_req)

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response

class MoreInfoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.MoreRests")(handler_input) and
                "curr_restaurant" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In MoreInfoIntentHandler")

        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        _ = attribute_manager.request_attributes["_"]

        restaurant_details = session_attr["curr_restaurant"]
        restaurant_categories = ", ".join(map(lambda x:x['title'], restaurant_details["categories"]))

        speech = ("{} is located at {}. It is rating {}, and it is "
                  "categorized as {}. I have sent these details to the "
                  "Alexa App on your phone.  Enjoy your meal! "
                  "<say-as interpret-as='interjection'>bon appetit</say-as>"
                  .format(restaurant_details["name"],
                          restaurant_details["display_address"][0],
                          restaurant_details["rating"],
                          restaurant_categories))
        card_info = "{}\naddress: {}\nphone: {}\ncategoires: {}".format(
            restaurant_details["name"], ", ".join(restaurant_details["display_address"]),
            restaurant_details["display_phone"], restaurant_categories)

        handler_input.response_builder.speak(speech).set_card(
            SimpleCard(
                title=_(data.SKILL_NAME),
                content=card_info)).set_should_end_session(True)
        return handler_input.response_builder.response


class SearchRestaurantsIntentHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("SearchRestaurantsIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        logger.info("In SearchRestaurantsIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        search_result = util.search(data.API_HOST, data.SEARCH_PATH, data.API_KEY, "London")['businesses']

        session_attr["num_of_search"] = 0
        session_attr["curr_restaurant"] = search_result.pop(0)
        session_attr["rest_restaurants"] = search_result

        logger.info(session_attr["curr_restaurant"])
        logger.info(session_attr["rest_restaurants"])

        speech = ("I find a place nearyby, called {}. "
                  "Do you want more information about it?  "
                  "Or do you want another suggestion?"
                  "<say-as interpret-as='interjection'>bon appetit</say-as>"
                  .format(session_attr["curr_restaurant"]["name"]))

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response

class AnotherRestaurantsIntentHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        return (is_request_type("AnotherRestaurantsIntent")(handler_input) and
                "rest_restaurants" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        logger.info("In AnotherRestaurantsIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        if not session_attr["rest_restaurants"]:
            session_attr["num_of_search"] = session_attr["num_of_search"] + 1
            search_result = util.search(data.API_HOST, data.SEARCH_PATH, data.API_KEY,
                            session_attr["location"], session_attr["num_of_search"])['businesses']

        session_attr["curr_restaurant"] = search_result.pop()
        session_attr["rest_restaurants"] = search_result

        logger.info(session_attr["curr_restaurant"])
        logger.info(session_attr["rest_restaurants"])

        speech = ("I find another place nearyby, called {}. "
                  "Do you want more information about it?  "
                  "Or do you want another suggestion?"
                  "<say-as interpret-as='interjection'>bon appetit</say-as>"
                  .format(session_attr["curr_restaurant"]["name"]))

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response



'''
class AskIfWantSpecifyIntentHandler(AbstractRequestHandler):
    """Handler for adding AskIfWantSpecify intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddAskIfWantSpecifyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AddIfWantSpecifyIntentHandler")
        cuisine = util.get_resolved_value(
            handler_input.request_envelope.request, "cuisine")
        if cuisine is None:
            cuisine = "ANYTHING"
            speech = ("I will choose a random cuisine.")
        else:
            speech = ("You want to eat {} food.").format(cuisine)

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response

class AddRestaurantCuisineIntentHandler(AbstractRequestHandler):
    """Handler for adding AddRestaurantCuisine intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddRestaurantCuisineIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AddRestaurantCuisineIntentHandler")
        global cuisine
        cuisine = util.get_resolved_value(
            handler_input.request_envelope.request, "cuisine")
        if cuisine is None:
            cuisine = "ANYTHING"
            speech = ("I will choose a random cuisine.")
        else:
            speech = ("You want to eat {} food.").format(cuisine)

        handler_input.response_builder.speak(speech).set_should_end_session(
            False)
        return handler_input.response_builder.response

'''
class YesMoreInfoIntentHandler(AbstractRequestHandler):
    """Handler for yes to get more info intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.YesIntent")(handler_input) and
                "restaurant" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In YesMoreInfoIntentHandler")

        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        _ = attribute_manager.request_attributes["_"]

        restaurant_name = session_attr["restaurant"]
        restaurant_details = util.get_restaurants_by_name(
            data.CITY_DATA, restaurant_name)

        speech = ("{} is located at {}, the phone number is {}, and the "
                  "description is, {}. I have sent these details to the "
                  "Alexa App on your phone.  Enjoy your meal! "
                  "<say-as interpret-as='interjection'>bon appetit</say-as>"
                  .format(restaurant_details["name"],
                          restaurant_details["address"],
                          restaurant_details["phone"],
                          restaurant_details["description"]))
        card_info = "{}\n{}\n{}, {}, {}\nphone: {}\n".format(
            restaurant_details["name"], restaurant_details["address"],
            data.CITY_DATA["city"], data.CITY_DATA["state"],
            data.CITY_DATA["postcode"], restaurant_details["phone"])

        handler_input.response_builder.speak(speech).set_card(
            SimpleCard(
                title=_(data.SKILL_NAME),
                content=card_info)).set_should_end_session(True)
        return handler_input.response_builder.response


class NoMoreInfoIntentHandler(AbstractRequestHandler):
    """Handler for no to get no more info intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.NoIntent")(handler_input) and
                "restaurant" in session_attr)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NoMoreInfoIntentHandler")

        speech = ("Ok.  Enjoy your meal! "
                  "<say-as interpret-as='interjection'>bon appetit</say-as>")
        handler_input.response_builder.speak(speech).set_should_end_session(
            True)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        logger.info("Session ended with reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        handler_input.response_builder.speak(_(
            data.HELP)).ask(_(data.HELP))
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop intents."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        handler_input.response_builder.speak(_(
            data.STOP)).set_should_end_session(True)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent or Yes/No without
    restaurant info intent.

     2018-May-01: AMAZON.FallackIntent is only currently available in
     en-US locale. This handler will not be triggered except in that
     locale, so it can be safely deployed for any locale."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("AMAZON.FallbackIntent")(handler_input) or
                ("restaurant" not in session_attr and (
                        is_intent_name("AMAZON.YesIntent")(handler_input) or
                        is_intent_name("AMAZON.NoIntent")(handler_input))
                 ))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]

        handler_input.response_builder.speak(_(
            data.FALLBACK).format(data.SKILL_NAME)).ask(_(
            data.FALLBACK).format(data.SKILL_NAME))

        return handler_input.response_builder.response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.

    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        logger.info("Original request was {}".format(
            handler_input.request_envelope.request))

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


class LocalizationInterceptor(AbstractRequestInterceptor):
    """Add function to request attributes, that can load locale specific data."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        i18n = gettext.translation(
            'base', localedir='locales', languages=[locale], fallback=True)
        handler_input.attributes_manager.request_attributes[
            "_"] = i18n.gettext


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AboutIntentHandler())
sb.add_request_handler(AddCityIntentHandler())
sb.add_request_handler(GetCityIntentHandler())
#sb.add_request_handler(AskIfWantSpecifyIntentHandler())
#sb.add_request_handler(AddRestaurantCuisineIntentHandler())
sb.add_request_handler(AddDietaryRequirementsIntentHandler())
sb.add_request_handler(GetDietaryRequirementsIntentHandler())
sb.add_request_handler(YesMoreInfoIntentHandler())
sb.add_request_handler(NoMoreInfoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(SearchRestaurantsIntentHandler())
#sb.add_request_handler(MoreInfoIntentHandler())
sb.add_request_handler(AnotherRestaurantsIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add locale interceptor to the skill.
sb.add_global_request_interceptor(LocalizationInterceptor())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
