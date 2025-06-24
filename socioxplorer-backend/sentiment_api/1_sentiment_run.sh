#!/bin/bash
gunicorn -b 0.0.0.0:10077 -t 1000 analyser_main:app --workers=2 --thread 4
