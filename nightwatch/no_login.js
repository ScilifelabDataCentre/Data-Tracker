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

  test('Test Dataset Info Page', function (browser) {
    browser
      .click('#index-q-card-datasets')
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
