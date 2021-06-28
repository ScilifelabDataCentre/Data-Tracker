describe('Data Tracker - Collections', function() {
  test('Collection Browser - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .setValue('input[type=search]', 'Frontend Test Collection')
      .waitForElementVisible('#entry-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-21c8ecd1-9908-462f-ba84-3ca399074b36', 'Frontend Test Collection')
      .click('#entry-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/collections/21c8ecd1-9908-462f-ba84-3ca399074b36');
  });

  test('Collection info page - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/collections/21c8ecd1-9908-462f-ba84-3ca399074b36')
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
