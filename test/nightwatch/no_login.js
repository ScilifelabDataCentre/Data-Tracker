describe('Data Tracker - not logged in', function() {

  test('Test basic details', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.titleContains('Data Tracker')
      .assert.elementPresent('.q-header')
      .assert.elementPresent('.q-drawer')
      .assert.elementPresent('.q-page');
  });

  test('Check first page content', function (browser) {
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

  test('Check drawer content and navigation', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')

      .click("#header-toggle-drawer")
      .pause(300)
      .assert.cssClassPresent('.q-drawer', 'q-layout--prevent-focus')
      .click("#header-toggle-drawer")
      .pause(300)
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
  
  test('Test dataset browser and info page', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .setValue('input[type=search]', 'Frontend Test Dataset')
      .waitForElementVisible('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1', 'Frontend Test Dataset')
      .click('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/datasets/79a755f1-69b0-4734-9977-ac945c4c51c1')

      .assert.containsText('#entry-about-title-text', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-title-identifier', '79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-tags', 'Frontend')
      .assert.containsText('#entry-about-tags', 'Test')
      .assert.containsText('#entry-about-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-about-properties .q-chip__content', 'Frontend Test Entry')
      .assert.containsText('#entry-about-description', 'A dataset added for frontend tests')

      .assert.not.elementPresent('#entry-about-datasets')

      .assert.containsText('#entry-about-related-0', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-related-0', '27cc1144-67bf-45b2-af21-425f9bfc7333')

      .assert.containsText('#entry-about-collections-0', 'Frontend Test Collection')
      .assert.containsText('#entry-about-collections-0', '21c8ecd1-9908-462f-ba84-3ca399074b36')
    
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

      .click('#entry-about-related-0')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/datasets/27cc1144-67bf-45b2-af21-425f9bfc7333')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-title-identifier', '27cc1144-67bf-45b2-af21-425f9bfc7333')

      .click('#entry-about-collections-0')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/collections/21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Collection')
      .assert.containsText('#entry-about-title-identifier', '21c8ecd1-9908-462f-ba84-3ca399074b36')
  });

  test('Test collection browser and info page', function (browser) {
    browser
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .setValue('input[type=search]', 'Frontend Test Collection')
      .waitForElementVisible('#entry-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-21c8ecd1-9908-462f-ba84-3ca399074b36', 'Frontend Test Collection')
      .click('#entry-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Collection')
      .assert.containsText('#entry-about-title-identifier', '21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-about-tags', 'Frontend')
      .assert.containsText('#entry-about-tags', 'Test')
      .assert.containsText('#entry-about-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-about-properties .q-chip__content', 'Frontend Test Entry')
      .assert.containsText('#entry-about-description', 'A collection added for frontend tests')

      .assert.containsText('#entry-about-datasets-0', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-datasets-0', '79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-datasets-1', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-datasets-1', '27cc1144-67bf-45b2-af21-425f9bfc7333')

      .assert.not.elementPresent('#entry-about-related')
      .assert.not.elementPresent('#entry-about-collections')
      .assert.not.elementPresent('#entry-about-authors')
      .assert.not.elementPresent('#entry-about-generators')
      .assert.not.elementPresent('#entry-about-organisation')
      .assert.not.elementPresent('#entry-about-editors')
  });
  
  after(browser => browser.end());
});
