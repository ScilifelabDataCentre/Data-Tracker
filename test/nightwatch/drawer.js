describe('Data Tracker - Side Drawer', function() {

  test('Open/close drawer', function (browser) {
    browser
      .url('http://localhost:5000')
      .waitForElementVisible('.q-page')

      .click("#header-toggle-drawer")
      .pause(300)
      .assert.cssClassPresent('.q-drawer', 'q-layout--prevent-focus')
      .click("#header-toggle-drawer")
      .pause(300)
      .assert.not.cssClassPresent('.q-drawer', 'q-layout--prevent-focus')
  });
  
  test('Not logged in', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000')
      .waitForElementVisible('.q-page')

      .assert.not.elementPresent('#drawer-entry-orders')

      .assert.elementPresent('#drawer-entry-datasets')
      .click('#drawer-entry-datasets')
      .assert.urlEquals('http://localhost:5000/datasets/')

      .assert.elementPresent('#drawer-entry-collections')
      .click('#drawer-entry-collections')
      .assert.urlEquals('http://localhost:5000/collections/')

      .assert.not.elementPresent('#drawer-entry-users')

      .assert.elementPresent('#drawer-entry-about')
      .click('#drawer-entry-about')
      .assert.urlEquals('http://localhost:5000/about')

      .assert.elementPresent('#drawer-entry-guide')
      .click('#drawer-entry-guide')
      .assert.urlEquals('http://localhost:5000/guide')

      .assert.not.elementPresent('#drawer-entry-current-user')

      .assert.elementPresent('#drawer-entry-log-in')
      .click('#drawer-entry-log-in')
      .assert.urlEquals('http://localhost:5000/login')

      .assert.not.elementPresent('#drawer-entry-log-out');
  });

  test('Basic User', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/author::frontend')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')

      .assert.not.elementPresent('#drawer-entry-orders')
      .assert.elementPresent('#drawer-entry-datasets')
      .assert.elementPresent('#drawer-entry-collections')
      .assert.not.elementPresent('#drawer-entry-users')
      .assert.elementPresent('#drawer-entry-about')
      .assert.elementPresent('#drawer-entry-guide')

      .assert.elementPresent('#drawer-entry-current-user')
      .click('#drawer-entry-current-user')
      .assert.urlEquals('http://localhost:5000/account/')

      .assert.not.elementPresent('#drawer-entry-log-in')
      .assert.elementPresent('#drawer-entry-log-out');
  });

  test('Edit User', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/generator::frontend')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')

      .assert.elementPresent('#drawer-entry-orders')
      .click('#drawer-entry-orders')
      .assert.urlEquals('http://localhost:5000/orders/')

      .assert.elementPresent('#drawer-entry-datasets')
      .assert.elementPresent('#drawer-entry-collections')
      .assert.not.elementPresent('#drawer-entry-users')
      .assert.elementPresent('#drawer-entry-about')
      .assert.elementPresent('#drawer-entry-guide')
      .assert.elementPresent('#drawer-entry-current-user')
      .assert.not.elementPresent('#drawer-entry-log-in')
      .assert.elementPresent('#drawer-entry-log-out');
  });

  test('Data/User Management User', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/organisation::frontend')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')

      .assert.elementPresent('#drawer-entry-orders')
      .assert.elementPresent('#drawer-entry-datasets')
      .assert.elementPresent('#drawer-entry-collections')

      .assert.elementPresent('#drawer-entry-users')
      .click('#drawer-entry-users')
      .assert.urlEquals('http://localhost:5000/admin/user')

      .assert.elementPresent('#drawer-entry-about')
      .assert.elementPresent('#drawer-entry-guide')
      .assert.elementPresent('#drawer-entry-current-user')
      .assert.not.elementPresent('#drawer-entry-log-in')
      .assert.elementPresent('#drawer-entry-log-out');
  });
    
  after(browser => browser.end());
});
