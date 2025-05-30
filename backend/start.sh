#!/bin/bash
@echo off
gunicorn --bind 0.0.0.0:5000 app:app