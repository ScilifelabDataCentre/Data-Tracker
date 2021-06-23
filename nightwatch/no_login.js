describe('Data Tracker - not logged in', function() {

  test('Test Basic Details', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.titleContains('Data Tracker')
      .assert.elementPresent('.q-header')
      .assert.elementPresent('.q-drawer')
      .assert.elementPresent('.q-page');
  });

  test('Check First Page Content', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.not.elementPresent('#index-card-orders')
      .click('#index-card-datasets')
      .assert.urlEquals('http://localhost:5000/datasets/')
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .click('#index-card-collections')
      .assert.urlEquals('http://localhost:5000/collections/');
  });

  test('Check Drawer Content and Navigation', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')

      .click("#header-toggle-drawer")
      .pause(500)
      .assert.cssClassPresent('.q-drawer', 'q-layout--prevent-focus')
      .click("#header-toggle-drawer")
      .pause(500)
      .assert.not.cssClassPresent('.q-drawer', 'q-layout--prevent-focus')

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
  
  test('Test Dataset Info Page', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .setValue('input[type=search]', 'Frontend Test Dataset')
      .waitForElementVisible('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1', 'Frontend Test Dataset')
      .click('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('.q-tab-panel h1')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-title-identifier', '79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-tags', 'Frontend')
      .assert.containsText('#entry-about-tags', 'Test')
      .assert.containsText('#entry-about-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-about-properties .q-chip__content', 'Frontend Test Entry')
      .assert.containsText('#entry-about-description', 'A dataset added for frontend tests')

      .assert.containsText('#entry-about-authors-0', 'Frontend Author')
      .assert.not.containsText('#entry-about-authors-0', 'author@frontend.dev')
      .click('#entry-about-authors-0 .q-focusable')
      .assert.containsText('#entry-about-authors-0', 'author@frontend.dev')
      .assert.containsText('#entry-about-authors-0', 'Frontend Test University')
      .assert.containsText('#entry-about-authors-0', 'https://www.example.com/frontend_author')
      .click('#entry-about-authors-0 .q-focusable')
      .assert.not.containsText('#entry-about-authors-0', 'author@frontend.dev')

      .assert.containsText('#entry-about-generators', 'Frontend Generator')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')
      .click('#entry-about-generators-0 .q-focusable')
      .assert.containsText('#entry-about-generators', 'generator@frontend.dev')
      .assert.containsText('#entry-about-generators', 'Frontend Test University')
      .assert.containsText('#entry-about-generators', 'https://www.example.com/frontend_generator')
      .click('#entry-about-generators-0 .q-focusable')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')

      .assert.containsText('#entry-about-organisation', 'Frontend Organisation')
      .assert.not.containsText('#entry-about-organisation', 'organisation@frontend.dev')
      .click('#entry-about-organisation .q-focusable')
      .assert.containsText('#entry-about-organisation', 'organisation@frontend.dev')
      .assert.containsText('#entry-about-organisation', 'Frontend Test University')
      .assert.containsText('#entry-about-organisation', 'https://www.example.com/frontend_organisation')
      .click('#entry-about-organisation .q-focusable')
      .assert.not.containsText('#entry-about-organisation', 'organisation@frontend.dev')

      .assert.not.elementPresent('#entry-about-editors')
  });
  
  after(browser => browser.end());
});
