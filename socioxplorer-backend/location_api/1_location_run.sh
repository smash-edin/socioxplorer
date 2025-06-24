#!/bin/bash
gunicorn -b 0.0.0.0:10066 -t 1000 location_api:app --workers=2 --thread 4
