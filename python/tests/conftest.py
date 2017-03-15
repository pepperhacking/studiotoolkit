# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:20:32 2017

@author: ekroeger
"""

import stk.runner
import stk.services

import pytest

def pytest_addoption(parser):
    parser.addoption("--qiurl", action="store",
        help="URL of the robot to connect to")

g_qiapp = None

@pytest.fixture
def qiapp(request):
    global g_qiapp
    if not g_qiapp:
        qiurl = request.config.getoption("--qiurl")
        g_qiapp =  stk.runner.init(qiurl)
    return g_qiapp

@pytest.fixture
def services(request):
    _qiapp = qiapp(request)
    return stk.services.ServiceCache(_qiapp.session)

