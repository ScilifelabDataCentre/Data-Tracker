describe('Data Tracker - basic user', function() {

  before(browser => {
    browser.url('http://localhost:5000/api/v1/developer/login/base::testers');
    browser.url('http://localhost:5000/')
  });

  test('Test Basic Details', function (browser) {
    browser
      .waitForElementVisible('body')
      .assert.titleContains('Data Tracker')
      .assert.elementPresent('.q-header')
      .assert.elementPresent('.q-drawer')
      .assert.elementPresent('.q-page');
  });

  test('Check First Page Content', function (browser) {
    browser
      .waitForElementVisible('body')
      .assert.containsText('.q-page', 'Datasets')
      .assert.containsText('.q-page', 'Collections')
      .assert.not.containsText('.q-page', 'Orders');
  });

  test('Check Drawer Content', function (browser) {
    browser
      .waitForElementVisible('body')
      .assert.not.containsText('.q-drawer', 'Orders')
      .assert.containsText('.q-drawer', 'Datasets')
      .assert.containsText('.q-drawer', 'Collections')
      .assert.not.containsText('.q-drawer', 'Users')
      .assert.containsText('.q-drawer', 'About the Data Tracker')
      .assert.containsText('.q-drawer', 'User Guide')
      .assert.containsText('.q-drawer', 'Current User')
      .assert.not.containsText('.q-drawer', 'Log In')
      .assert.containsText('.q-drawer', 'Log Out')
  });
  
  after(browser => browser.end());
});
