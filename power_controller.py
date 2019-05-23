#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to control power of a machine using GPIO

Dependencies:
    apt-get install python3-rpi.gpio
"""
import imp
import logging
import os
import sys
import time
import RPi.GPIO as GPIO

__version__ = '1.0'
logger = logging.getLogger('power_controller')


class PowerController():
    CONF_PATH = os.path.expanduser('~/.power_controller.py')
    CONF = {
        'LOG_LEVEL': 'INFO',
        'LED_GPIO': 16,
        'SYSTEMS': [
            {'gpio_on': 21, 'gpio_reboot': 20, 'label': 'Test machine'},
        ],
    }

    def __init__(self, *args):
        self.display_header()
        # Setup logging
        log_format = '%(asctime)s %(name)s %(levelname)s %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        # Read conf file
        if os.path.exists(self.CONF_PATH):
            try:
                conf = imp.load_source('conf', self.CONF_PATH)
            except ImportError as e:
                logger.error('Unable to load config file %s: %s', self.CONF_PATH, e)
            else:
                logger.info('Config file loaded.')
                for key in dir(conf):
                    if not key.startswith('_'):
                        self.CONF[key] = getattr(conf, key)
        # Configure logging
        level = getattr(logging, self.CONF['LOG_LEVEL']) if self.CONF.get('LOG_LEVEL') else logging.INFO
        root_logger = logging.getLogger('root')
        root_logger.setLevel(level)
        logger.setLevel(level)
        logging.captureWarnings(False)
        logger.debug('Logging conf set.')
        # Setup GPIO
        self.setup_gpio()
        # Load conf
        if args:
            # Run command
            for arg in args:
                self.run(arg, interactive=False)
        else:
            # Open main menu
            self.menu()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.CONF['LED_GPIO'], GPIO.OUT)
        for system in self.CONF['SYSTEMS']:
            GPIO.setup(system['gpio_on'], GPIO.OUT)
            GPIO.setup(system['gpio_reboot'], GPIO.OUT)

    def display_header(self):
        title = '- Power controller -'
        print('\n\033[96m%s\033[0m' % ('-' * len(title)))
        print('\033[96m%s\033[0m' % title)
        print('\033[96m%s\033[0m\n' % ('-' * len(title)))

    def menu(self):
        # Show main menu
        print('Actions:')
        for index, system in enumerate(self.CONF['SYSTEMS']):
            print('  %s1: %s' % (index + 1, 'Power on "%s"' % system['label']))
            print('  %s2: %s' % (index + 1, 'Power off "%s"' % system['label']))
            print('  %s3: %s' % (index + 1, 'Reboot "%s"' % system['label']))
        print('  e: Exit\n')
        print('Info:')
        print('\nWhat action do you want to start ?')
        try:
            target = input('---> ').strip()
        except (KeyboardInterrupt, EOFError):
            print()
            target = 'e'
        self.run(target)

    def run(self, target, interactive=True):
        if target == 'e':
            print('Exit')
            GPIO.cleanup()
            sys.exit(0)
        else:
            found = False
            for index, system in enumerate(self.CONF['SYSTEMS']):
                if target == '%s1' % (index + 1):
                    self.power_on(system)
                elif target == '%s2' % (index + 1):
                    self.power_off(system)
                elif target == '%s3' % (index + 1):
                    self.reboot(system)
                else:
                    continue
                found = True
            if not found:
                print('Invalid action requested')
        if interactive:
            print('\n')
            self.menu()
        else:
            GPIO.cleanup()
            sys.exit(0)

    def set_pin(self, pin, val):
        GPIO.output(self.CONF['LED_GPIO'], 1 if val else 0)
        GPIO.output(pin, 1 if val else 0)

    def power_on(self, system):
        print('    Powering on "%s" (pin %s).' % (system['label'], system['gpio_on']))
        self.set_pin(system['gpio_on'], 1)
        time.sleep(1)
        self.set_pin(system['gpio_on'], 0)
        print('Done')

    def power_off(self, system):
        print('    Shutting down "%s" (pin %s).' % (system['label'], system['gpio_on']))
        self.set_pin(system['gpio_on'], 1)
        time.sleep(6)
        self.set_pin(system['gpio_on'], 0)
        print('Done')

    def reboot(self, system):
        print('    Rebooting "%s" (pin %s).' % (system['label'], system['gpio_reboot']))
        self.set_pin(system['gpio_reboot'], 1)
        time.sleep(1)
        self.set_pin(system['gpio_reboot'], 0)
        print('Done')


if __name__ == '__main__':
    PowerController(*sys.argv[1:])
