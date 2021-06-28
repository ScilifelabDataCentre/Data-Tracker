describe('Data Tracker - Datasets', function() {
  test('Dataset Browser - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .setValue('input[type=search]', 'Frontend Test Dataset')
      .waitForElementVisible('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1', 'Frontend Test Dataset')
      .click('#entry-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/datasets/79a755f1-69b0-4734-9977-ac945c4c51c1')
  });

  test('Dataset info page - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/datasets/79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-title-identifier', '79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-tags', 'Frontend')
      .assert.containsText('#entry-about-tags', 'Test')
      .assert.containsText('#entry-about-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-about-properties .q-chip__content', 'Frontend Test Entry')
      .assert.containsText('#entry-about-description', 'A dataset added for frontend tests')

      .assert.not.elementPresent('#entry-about-order')
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
  
  after(browser => browser.end());
});
