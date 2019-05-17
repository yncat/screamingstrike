# -*- coding: utf-8 -*-
# NsSpeechSynthesizer output
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

from __future__ import absolute_import

from .base import Output
from Cocoa import NSSpeechSynthesizer
class NSSpeechSynth(Output):

	"""Speech output supporting the Apple built-in tts, which is independent from voiceover."""

	name = 'NSSpeechSynthesizer'
	def __init__(self, *args, **kwargs):
		self.speechSynthesizer = NSSpeechSynthesizer.alloc().initWithVoice_(None)

	def speak(self, text, interrupt=False):
		self.speechSynthesizer.startSpeakingString_(text)

	def silence (self):
		self.speechSynthesizer.startSpeakingString_("")

	def is_active(self):
		return True

output_class = NSSpeechSynth
