"""
kivy/uix/nativetextinput.py
============================

NativeTextInput — a drop-in replacement for TextInput that uses the native
Android IME instead of SDL on Android, while behaving identically to
TextInput on every other platform.

Why it exists
-------------
Kivy's classic TextInput routes all keyboard input through SDL2.  On Android
that means:

* The IME composing / commit protocol is not implemented -> broken CJK,
  broken predictive keyboards, broken gesture / swipe typing.
* Autocorrect underlines are ignored.
* The Done / Search action button does not fire on_text_validate.
* Physical keyboard arrow keys sometimes drop characters.

This widget fixes all of the above by replacing the SDL keyboard path with a
real Android View (``KivyKeyboardProxy.java``) that implements
``BaseInputConnection`` correctly, then translates the IME events back to the
existing Kivy TextInput API so the rest of Kivy remains unchanged.

On desktop / iOS / other platforms it is identical to TextInput.

Usage
-----
::

    from kivy.uix.nativetextinput import NativeTextInput

    # Use exactly like TextInput:
    ti = NativeTextInput(hint_text='Type here...', multiline=False)
    ti.bind(on_text_validate=lambda inst: print(inst.text))

KV language::

    #:import NativeTextInput kivy.uix.nativetextinput.NativeTextInput

    NativeTextInput:
        hint_text: 'Native keyboard on Android'
        multiline: False
        on_text_validate: print(self.text)

Buildozer
---------
Add the Java source directory so it gets compiled into the APK::

    android.add_java_dir = kivy/java
"""

from kivy.uix.behaviors.keyboard_proxy import AndroidKeyboardProxy
from kivy.uix.textinput import TextInput

__all__ = ('NativeTextInput',)


class NativeTextInput(AndroidKeyboardProxy, TextInput):
    """
    Drop-in replacement for :class:`~kivy.uix.textinput.TextInput`.

    On Android the soft keyboard is managed by ``KivyKeyboardProxy.java``
    (a real ``BaseInputConnection`` view) instead of SDL2, which fixes all
    long-standing IME issues.  On all other platforms this is identical to
    :class:`~kivy.uix.textinput.TextInput`.

    All TextInput properties, events and methods are available as-is.
    """
    pass
