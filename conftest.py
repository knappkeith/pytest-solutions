import pytest
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from elements.quickbooks_desktop import QuickBooksDesktop
import libs.formulas as formulas
from libs.requests_wrapper import CeElementRequests

sys.path.append(os.path.abspath(os.path.curdir))

@pytest.fixture(scope="session", autouse=True)
def set_up_test_run(request):
    """
        Setup the test run, always use, entire session.
    """
    # Add the current directory, which should be the overall directory for the
    #   project to the system path for Python so that modules can be imported
    #   by from CURDIR.SUBFOLDER.MODULE import CLASS/FUNCTION
    # print "\nSet Up: Cur Dir: %s" % os.path.abspath(os.path.curdir)
    # print "\nCur sys.path: %s"
    # for i in sys.path:
    #     print i

    sys.path.append(os.path.abspath(os.path.curdir))
    # sys.path.append(os.path.abspath(os.path.curdir))
    # print "\nNew sys.path:"
    # for i in sys.path:
    #     print i

    def tear_down_test_run():
        # This function really doesn't do anything at this point but will be
        #   used to tear down anything for the overall session in the future.
        pass
    request.addfinalizer(tear_down_test_run)


@pytest.yield_fixture(scope="function")
def quickbooks_desktop_element(request):
    from libs.elements import QuickBooksDesktop
    
    if hasattr(request.module, 'ELEMENT_CONFIG'):
        element_config = request.module.ELEMENT_CONFIG['quickbooks_desktop']
    else:
        element_config = {}
    session = QuickBooksDesktop(**element_config)
    yield session


@pytest.yield_fixture(scope="function")
def dynamics_crm_element(request):
    from libs.elements import DynamicsCRM
    
    if hasattr(request.module, 'ELEMENT_CONFIG'):
        element_config = request.module.ELEMENT_CONFIG['dynamics_crm']
    else:
        element_config = {}
    session = DynamicsCRM(**element_config)
    yield session


@pytest.yield_fixture(scope="function")
def browser(request):
    """
        Yield a browser, type of browser specied by cmdopt --browser
    """
    browser = _get_driver(browser=request.config.option.browser)
    browser.set_env_var(request_object=request)
    browser.timer.lap("Browser setup")
    yield browser
    try:
        browser.quit()
    except:
        print "There was an issue quitting the broswer!"


def _get_driver(browser="chrome", include_logging=True):
    """
        Return the driver of the passed type.

        include_logging - sets up desired_capabilities for the browser to allow
                          logging to be obtained
    """
    profile = None
    capabilities = None
    if browser == "firefox":
        if include_logging:
            profile = webdriver.FirefoxProfile()
            profile.add_extension(
                os.path.join(_get_current_directory(),
                             'utils/consoleExport-0.5b5.xpi'))
            profile.add_extension(
                os.path.join(_get_current_directory(),
                             'utils/firebug-2.0.11-fx.xpi'))
            capabilities = DesiredCapabilities.FIREFOX
            capabilities['loggingPrefs'] = {'browser': 'ALL'}
        return selenium_wrapper.Selenium_Wrapper_Firefox(
            capabilities=capabilities,
            firefox_profile=profile)
    elif browser == "chrome":
        if include_logging:
            capabilities = DesiredCapabilities.CHROME
            capabilities['loggingPrefs'] = {'browser': 'ALL'}
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chromedriver_path = os.path.join(
            _get_current_directory(),
            'utils/chromedriver')
        driver = selenium_wrapper.Selenium_Wrapper_Chrome(
            desired_capabilities=capabilities,
            executable_path=chromedriver_path,
            chrome_options=chrome_options)
        driver.maximize_window()
        return driver
    elif browser == 'headless' or browser == "phantomjs":
        capabilities = DesiredCapabilities.PHANTOMJS
        if include_logging:
            capabilities['loggingPrefs'] = {'browser': 'ALL'}
        capabilities['phantomjs.page.settings.userAgent'] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36")
        driver = selenium_wrapper.Selenium_Wrapper_PhantomJS(
                desired_capabilities=capabilities,
                service_args=["--ignore-ssl-errors=yes"])

        # This is need for a bug using PhantomJS and selenium where nothing
        #   will be visable
        driver.set_window_size(1120, 550)
        return driver


def _get_current_directory():
    """
        Return the Value of the current directory of this file.
    """
    return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


def pytest_addoption(parser):
    """
        Add command line arguements here.
    """
    parser.addoption("--env",
                     action="store",
                     default='snapshot',
                     help="execute tests on specific environment, dev | staging | prod.")
    parser.addoption("--browser",
                     action="store",
                     default='chrome',
                     help="execute tests with passed browser, firefox | chrome | headless(PhantomJS).")
    parser.addoption("--all_tests",
                     action="store_false",
                     help="execute all tests, including tests that are under development.")


def pytest_configure(config):
    """
        Configuring py.test, add items here for ini, help and things like that
    """
    # register an additional marker
    config.addinivalue_line("markers",
                            "dev: mark tests that are still under development")


def pytest_runtest_setup(item):
    if item.config.getoption("--all_tests"):
        is_dev = item.get_marker("dev")
        if is_dev is not None:
            pytest.skip("Test still under development, use --all_tests cmdopt to run.")
