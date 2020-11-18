# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.dialog import (
    ElicitSlotDirective, DelegateDirective)
from ask_sdk_model import (
    Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
from ask_sdk_core.utils import is_intent_name, get_dialog_state, get_slot_value

from ask_sdk_model import Response
import json
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


bar_features={'categories':[],'values':[]}
def bar_attribute_list(position):
    bar_features['categories'].append(eval(json.loads(json.dumps(str(position['Label']))))['value'])
    bar_features['values'].append(int(eval(json.loads(json.dumps(str(position['Value']))))['value']))

url = "https://e56b860989d4.ngrok.io/"

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "What do you want to build?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        print("Hello Intent")
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder.response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder.response
        )


class CreatePPTSubjectCountIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CreatePPTSubjectCountIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "You can say hello to me!"
        slots = handler_input.request_envelope.request.intent.slots
        subject = slots['subject'].value
        count = slots['count'].value
        source = slots['source'].value
        if int(count) > 0:
            data = {
                "req": "create_ppt_count",
                "title": subject,
                "count": int(count),
                "source": source
            }
        else:
            data = {
                "req": "create_ppt",
                "title": subject,
                "source": source
            }

        success = False
        response = None
        try:
            response = requests.post(url=url, json=data)
            if response.status_code == 200:
                response = response.json()
                success = True
            elif response.status_code == 404:
                success = False
        except Exception as err:
            print(f'Error occurred: {err}')
            success = False

        if success:
            speech_output = "Created a presentation of " + str(response["count"]) + " slides on " + response["title"]
            reprompt_text = "I said presentation of " + str(response["count"]) + " slides on " + response[
                "title"] + " is created "
            should_end_session = False
        else:
            speech_output = "Cannot create a presentation on " + subject
            reprompt_text = "I said I was not able to create a presentation on " + subject

            should_end_session = False
        # global topic, slides
        # slots = handler_input.request_envelope.request.intent.slots
        # topic = slots['Topic'].value
        # slides = slots['Slides'].value
        return handler_input.response_builder.speak("Which type of chart do you want? Barchart or Line chart or Pie chart?").response

class CreateTeamSlideIntent(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CreateTeamSlideIntent")(handler_input)

    def handle(self, handler_input):
        card_title = "TeamSlide"

        data = {
            "req": "create_team_slide",
            "people": []
        }
        slots = handler_input.request_envelope.request.intent.slots

        slotPeople = eval(json.loads(json.dumps(str(slots['people']))))
        
        if 'values' in slotPeople['slot_value']:
            input_list = slotPeople["slot_value"]["values"]
            people = [i["value"] for i in input_list]
            data['people'] = people
        else:
            data["people"] = [slotPeople["slot_value"]["value"]]
        #     intent['slots']
        #     if 'value' in intent['slots']['people']:
        #         data["people"] = [intent['slots']['people']['value']]
        #     else:
        #         input_list = intent['slots']['people']['slotValue']['values']
        #         people = [i["value"] for i in input_list]
        #         data["people"] = people
        # except Exception as err:
        #     print(f'Cannot access people: {err}')
        print("This is team slide data: ", type(data["people"]))
        response = requests.post(url=url, json=data)
        response = response.json()
        speech_output = response["message"]
        reprompt_text = "I said " + speech_output
        should_end_session = False

        return handler_input.response_builder.speak(speech_output).response


class BarchartHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):

        return ask_utils.is_intent_name("Barchart")(handler_input)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes

        if session_attr:
            pos = session_attr['Position']
            pos = int(pos)
            # print(pos)
            bar_features['Label'][pos] = eval(json.loads(json.dumps(str(slots['Label']))))['value']
            bar_features['Value'][pos] = int(eval(json.loads(json.dumps(str(slots['Value']))))['value'])
            session_attr=None
        else:
            bar_attribute_list(slots)

        return handler_input.response_builder.speak("You have {} labels and {} values. Add/Update/Delete label-value pair or Stop to add other charts?".format(bar_features.keys(), bar_features.values())).response

class UpdatebarchartHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):

        intentRequest = handler_input.request_envelope.request
        return ask_utils.is_intent_name("Updatebarchart")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        pos = slots["Position"].value
        session_attr["Position"] = int(pos)

        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent="Barchart"
            )).response

class DeletebarchartHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Deletebarchart")(handler_input)

    def handle(self, handler_input):
        delete_position = int(handler_input.request_envelope.request.intent.slots['Position'].value)
        bar_features['Label'].pop(delete_position)
        bar_features['Value'].pop(delete_position)
        return handler_input.response_builder.speak("You have {} labels and {} values. Add/Update/Delete label-value pair or Stop to add other charts?".format(bar_features.keys(), bar_features.values())).response

line_features={'Label':[],'Value':[]}
def line_attribute_list(position):
    line_features['Label'].append(eval(json.loads(json.dumps(str(position['Label']))))['value'])
    line_features['Value'].append(int(eval(json.loads(json.dumps(str(position['Value']))))['value']))

class LinechartHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Linechart")(handler_input)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes

        if session_attr:
            pos = session_attr['Position']
            pos = int(pos)
            print(pos)
            line_features['Label'][pos] = eval(json.loads(json.dumps(str(slots['Label']))))['value']
            line_features['Value'][pos] = int(eval(json.loads(json.dumps(str(slots['Value']))))['value'])
            session_attr=None
        else:
            line_attribute_list(slots)

        return handler_input.response_builder.speak("You have {} labels and {} values. Add/Update/Delete label-value pair or Stop to add other charts?".format(line_features.keys(), line_features.values())).response

class UpdatelinechartHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        intentRequest = handler_input.request_envelope.request
        return ask_utils.is_intent_name("Updatelinechart")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        pos = slots["Position"].value
        session_attr["Position"] = int(pos)

        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent="Linechart"
            )).response

class DeletelinechartHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Deletelinechart")(handler_input)

    def handle(self, handler_input):
        delete_position = int(handler_input.request_envelope.request.intent.slots['Position'].value)
        line_features['Label'].pop(delete_position)
        line_features['Value'].pop(delete_position)
        return handler_input.response_builder.speak("You have {} labels and {} values. Add/Update/Delete label-value pair or Stop to add other charts?".format(line_features.keys(), line_features.values())).response

pie_features={'categories':[],'percentages':[]}
def pie_attribute_list(position):
    pie_features['categories'].append(eval(json.loads(json.dumps(str(position['Category']))))['value'])
    pie_features['percentages'].append(float(eval(json.loads(json.dumps(str(position['Percentag']))))['value']))

class PiechartHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Piechart")(handler_input)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes

        if session_attr:
            pos = session_attr['Position']

            pie_features['Category'][pos] = eval(json.loads(json.dumps(str(slots['Category']))))['value']
            pie_features['Percentages'][pos] = float(eval(json.loads(json.dumps(str(slots['Percentag']))))['value'])
            session_attr=None
        else:
            pie_attribute_list(slots)

        return handler_input.response_builder.speak("You have {} labels and {} values. Add/Update/Delete Category-Percentag pair or Stop to add other charts?".format(pie_features.keys(), pie_features.values())).response

class UpdatepiechartHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # intentRequest = handler_input.request_envelope.request
        intentRequest = handler_input.request_envelope.request
        return ask_utils.is_intent_name("Updatepiechart")(handler_input)

        # return ask_utils.is_intent_name("Presentationmaker")(handler_input) and intentRequest.dialog_state == 'COMPLETED'

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        pos = slots["Position"].value
        session_attr["Position"] = int(pos)
        #session_attr['Position'] = slots['Position'].value

        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent="Piechart"
            )).response

class DeletepiechartHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Deletepiechart")(handler_input)

    def handle(self, handler_input):
        delete_position = int(handler_input.request_envelope.request.intent.slots['Position'].value)
        pie_features['Category'].pop(delete_position)
        pie_features['Percentages'].pop(delete_position)
        return handler_input.response_builder.speak("You have {} labels and {} values. Add/Update/Delete Category-Percentag pair or Stop to add other charts?".format(pie_features.keys(), pie_features.values())).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Here is your presentation"

        return (
            handler_input.response_builder
                .speak("Do you want another type of chart or a teams slide?")
                .response
        )

class FinalizepresentationHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Finalizepresentation")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Here is your presentation"
        


        response = requests.post(url=url, json=data)
        response = response.json()
        return (
            handler_input.response_builder
                .speak(response['message'])
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
            handler_input.response_builder.speak(speak_output).response)


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

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CreatePPTSubjectCountIntent())
sb.add_request_handler(CreateTeamSlideIntent())
sb.add_request_handler(BarchartHandler())
sb.add_request_handler(UpdatebarchartHandler())
sb.add_request_handler(DeletebarchartHandler())
sb.add_request_handler(LinechartHandler())
sb.add_request_handler(UpdatelinechartHandler())
sb.add_request_handler(DeletelinechartHandler())
sb.add_request_handler(PiechartHandler())
sb.add_request_handler(UpdatepiechartHandler())
sb.add_request_handler(DeletepiechartHandler())
sb.add_request_handler(FinalizepresentationHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())
print(bar_features)
lambda_handler = sb.lambda_handler()
