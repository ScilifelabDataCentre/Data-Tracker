describe('Data Tracker - not logged in', function() {

  before(browser => browser.url('http://localhost:5000/'));

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
      .assert.containsText('#index-q-card-datasets', 'Datasets')
      .assert.containsText('#index-q-card-collections', 'Collections')
      .assert.not.containsText('.q-page', 'Orders');
  });

  test('Check Drawer Content', function (browser) {
    browser
      .assert.not.containsText('.q-drawer', 'Orders')
      .assert.containsText('.q-drawer', 'Datasets')
      .assert.containsText('.q-drawer', 'Collections')
      .assert.not.containsText('.q-drawer', 'Users')
      .assert.containsText('.q-drawer', 'About the Data Tracker')
      .assert.containsText('.q-drawer', 'User Guide')
      .assert.not.containsText('.q-drawer', 'Current User')
      .assert.containsText('.q-drawer', 'Log In')
      .assert.not.containsText('.q-drawer', 'Log Out')
  });

  test('Test Datasets', function (browser) {
    browser
      .click('#index-q-card-datasets')
      .waitForElementVisible('.q-table--grid')
      .setValue('input[type=search]', 'Dataset 500')
      .pause(1000)
      .assert.containsText('.q-table__grid-content', 'Dataset 500 Title')
      .click('.q-table__grid-content .q-card')
      .pause(10000)
  });
  
  after(browser => browser.end());
});
