describe('Data Tracker - Datasets', function() {
  test('Dataset Browser - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('#entry-browser-add')

      .setValue('input[type=search]', 'Frontend Test Dataset')
      .waitForElementVisible('#entry-d-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-d-79a755f1-69b0-4734-9977-ac945c4c51c1', 'Frontend Test Dataset')
      .click('#entry-d-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/datasets/d-79a755f1-69b0-4734-9977-ac945c4c51c1')
  });

  test('Dataset info page - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/datasets/d-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-uuid', 'd-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-tags', 'Frontend')
      .assert.containsText('#entry-about-tags', 'Test')
      .assert.containsText('#entry-about-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-about-properties .q-chip__content', 'Frontend Test Entry')
      .assert.containsText('#entry-about-description', 'A dataset added for frontend tests')

      .assert.not.elementPresent('#entry-about-order')
      .assert.not.elementPresent('#entry-about-datasets')

      .assert.containsText('#entry-about-related', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-related', 'd-27cc1144-67bf-45b2-af21-425f9bfc7333')

      .assert.containsText('#entry-about-collections', 'Frontend Test Collection')
      .assert.containsText('#entry-about-collections', 'c-21c8ecd1-9908-462f-ba84-3ca399074b36')
    
      .assert.containsText('#entry-about-authors', 'Frontend Author')
      .assert.not.containsText('#entry-about-authors', 'author@frontend.dev')
      .click('#entry-about-authors .q-focusable')
      .assert.containsText('#entry-about-authors', 'author@frontend.dev')
      .assert.containsText('#entry-about-authors', 'Frontend Test University')
      .assert.containsText('#entry-about-authors', 'https://www.example.com/frontend_author')
      .click('#entry-about-authors .q-focusable')
      .assert.not.containsText('#entry-about-authors', 'author@frontend.dev')

      .assert.containsText('#entry-about-generators', 'Frontend Generator')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')
      .click('#entry-about-generators .q-focusable')
      .assert.containsText('#entry-about-generators', 'generator@frontend.dev')
      .assert.containsText('#entry-about-generators', 'Frontend Test University')
      .assert.containsText('#entry-about-generators', 'https://www.example.com/frontend_generator')
      .click('#entry-about-generators .q-focusable')
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

      .click('#entry-about-related')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/datasets/d-27cc1144-67bf-45b2-af21-425f9bfc7333')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-uuid', 'd-27cc1144-67bf-45b2-af21-425f9bfc7333')

      .click('#entry-about-collections')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/collections/c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Collection')
      .assert.containsText('#entry-about-uuid', 'c-21c8ecd1-9908-462f-ba84-3ca399074b36')
  });

  test('Dataset info page - logged in (not editor)', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/generator::frontend')
      .url('http://localhost:5000/datasets/d-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.not.elementPresent('#entry-info-menu')
      .assert.not.elementPresent('#entry-about-editors')
      .assert.elementPresent('#entry-about-collections')
      .assert.not.elementPresent('#entry-about-order')
      .assert.not.elementPresent('#entry-about-datasets')
  });

  test('Dataset info page - logged in (editor)', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/editor::frontend')
      .url('http://localhost:5000/datasets/d-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .waitForElementVisible('#entry-about-title-text')
      .assert.elementPresent('#entry-info-menu')
      .assert.elementPresent('#entry-about-editors')
      .assert.elementPresent('#entry-about-collections')
      .assert.elementPresent('#entry-about-order')
      .assert.not.elementPresent('#entry-about-datasets')
  });
  
  
  test('Add dataset - start', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/editors::frontend')
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/datasets/add')
  });

  test('Add dataset - select order, load data', function (browser) {
    browser
      .click('#entry-edit-order-select tr div[role=checkbox]')
      .click('#entry-edit-order-select button[type=submit]')
      .assert.value('#entry-edit-title', 'Frontend Test Order')
      .click('#entry-edit-tags .q-item--clickable')
      .assert.containsText('#entry-edit-tags .q-chip', 'Frontend')
      .assert.containsText('#entry-edit-tags .q-chip:nth-of-type(2)', 'Test')
      .click('#entry-edit-tags .q-item--clickable')
      .click('#entry-edit-properties .q-item--clickable')
      .assert.containsText('#entry-edit-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-edit-properties .q-chip__content', 'Frontend Test Entry')
      .click('#entry-edit-properties .q-item--clickable')
      .assert.value('#entry-edit-description', 'An order added for frontend tests')
  });

  test('Add dataset - set fields', function (browser) {
    browser
      .setInputValue('#entry-edit-title', 'Dataset from frontend test')
      .setInputValue('#entry-edit-description', 'A dataset created during a frontend test run')

      .click('#entry-edit-tags .q-item--clickable')
      .setInputValue('#entry-edit-tags input', 'New Tag1')
      .keys('\uE006')
      .setInputValue('#entry-edit-tags input', 'New Tag2')
      .keys('\uE006')
      .click('#entry-edit-tags .q-item--clickable')

      .click('#entry-edit-properties .q-item--clickable')
      .setInputValue('#entry-edit-properties input', 'Key1')
      .keys('\uE006')
      .setInputValue('#entry-edit-properties input', 'Key2')
      .keys('\uE006')
      .setInputValue('#entry-edit-properties .q-list input[aria-label=Key1]', 'Value1')
      .setInputValue('#entry-edit-properties .q-list input[aria-label=Key2]', 'Value2')
      .click('#entry-edit-properties .q-item--clickable')
      .assert.not.visible('#entry-edit-properties input')

      .assert.not.elementPresent('#entry-edit-authors')
      .assert.not.elementPresent('#entry-edit-generators')
      .assert.not.elementPresent('#entry-edit-organisation')
      .assert.not.elementPresent('#entry-edit-datasets')
      .assert.not.elementPresent('#entry-edit-editors')
  });

  test('Test saving dataset', function (browser) {
    browser
      .click('#entry-save-button')
      .expect.url().to.match(/http:\/\/localhost:5000\/datasets\/d-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
  });

  test('Add/about dataset - validate fields', function (browser) {
    browser
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Dataset from frontend test')
      .expect.element('#entry-about-uuid').text.to.match(/d-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .assert.containsText('#entry-about-tags .q-chip', 'Frontend')
      .assert.containsText('#entry-about-tags .q-chip:nth-of-type(2)', 'Test')
      .assert.containsText('#entry-about-tags .q-chip:nth-of-type(3)', 'New Tag1')
      .assert.containsText('#entry-about-tags .q-chip:nth-of-type(4)', 'New Tag2')

      .assert.containsText('#entry-about-properties', 'Type')
      .assert.containsText('#entry-about-properties', 'Frontend Test Entry')
      .assert.containsText('#entry-about-properties', 'Key1')
      .assert.containsText('#entry-about-properties', 'Value1')
      .assert.containsText('#entry-about-properties', 'Key2')
      .assert.containsText('#entry-about-properties', 'Value2')
      .assert.containsText('#entry-about-description', 'A dataset created during a frontend test run')

      .assert.containsText('#entry-about-order', 'Frontend Test Order')
      .assert.containsText('#entry-about-order', 'o-d4467732-8ddd-43a6-a904-5b7376f60e5c')

      .assert.containsText('#entry-about-related', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-related', 'd-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-related', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-related', 'd-27cc1144-67bf-45b2-af21-425f9bfc7333')
    
      .assert.not.elementPresent('#entry-about-datasets')
      .assert.not.elementPresent('#entry-about-collections')
    
      .assert.containsText('#entry-about-authors', 'Frontend Author')
      .assert.not.containsText('#entry-about-authors', 'author@frontend.dev')
      .click('#entry-about-authors .q-focusable')
      .assert.containsText('#entry-about-authors', 'author@frontend.dev')
      .assert.containsText('#entry-about-authors', 'Frontend Test University')
      .assert.containsText('#entry-about-authors', 'https://www.example.com/frontend_author')
      .click('#entry-about-authors .q-focusable')
      .assert.not.containsText('#entry-about-authors', 'author@frontend.dev')

      .assert.containsText('#entry-about-generators', 'Frontend Generator')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')
      .click('#entry-about-generators .q-focusable')
      .assert.containsText('#entry-about-generators', 'generator@frontend.dev')
      .assert.containsText('#entry-about-generators', 'Frontend Test University')
      .assert.containsText('#entry-about-generators', 'https://www.example.com/frontend_generator')
      .click('#entry-about-generators .q-focusable')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')

      .assert.containsText('#entry-about-organisation', 'Frontend Organisation')
      .assert.not.containsText('#entry-about-organisation', 'organisation@frontend.dev')
      .click('#entry-about-organisation .q-focusable')
      .assert.containsText('#entry-about-organisation', 'organisation@frontend.dev')
      .assert.containsText('#entry-about-organisation', 'Frontend Test University')
      .assert.containsText('#entry-about-organisation', 'https://www.example.com/frontend_organisation')
      .click('#entry-about-organisation .q-focusable')
      .assert.not.containsText('#entry-about-organisation', 'organisation@frontend.dev')

      .assert.not.containsText('#entry-about-editors', 'editor@frontend.dev')
      .click('#entry-about-editors .q-focusable')
      .assert.containsText('#entry-about-editors', 'editor@frontend.dev')
      .assert.containsText('#entry-about-editors', 'Frontend Test University')
      .assert.containsText('#entry-about-editors', 'https://www.example.com/frontend_editor')
      .click('#entry-about-editors .q-focusable')
  });

  test('Enter edit mode', function (browser) {
    browser
      .click('#entry-info-menu')
      .click('#entry-info-menu-edit')
      .waitForElementVisible('#entry-edit-uuid')
      .assert.visible('#entry-save-button')
      .assert.visible('#entry-cancel-button')
      .assert.visible('div[role=tablist]')
  });
  
  test('Edit mode - data loaded correctly', function (browser) {
    browser
      .expect.element('#entry-edit-uuid').text.to.match(/d-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .assert.value('#entry-edit-title', 'Dataset from frontend test')
      .assert.value('#entry-edit-description', 'A dataset created during a frontend test run')    

      .click('#entry-edit-tags .q-item--clickable')
      .assert.containsText('#entry-edit-tags .q-chip', 'Frontend')
      .assert.containsText('#entry-edit-tags .q-chip:nth-of-type(2)', 'Test')
      .assert.containsText('#entry-edit-tags .q-chip:nth-of-type(3)', 'New Tag')
      .assert.containsText('#entry-edit-tags .q-chip:nth-of-type(4)', 'New Tag2')
      .click('#entry-edit-tags .q-item--clickable')

      .click('#entry-edit-properties .q-item--clickable')
      .assert.containsText('#entry-edit-properties', 'Type')
      .assert.containsText('#entry-edit-properties', 'Frontend Test Entry')
      .assert.containsText('#entry-edit-properties', 'Key1')
      .assert.containsText('#entry-edit-properties', 'Value1')
      .assert.containsText('#entry-edit-properties', 'Key2')
      .assert.containsText('#entry-edit-properties', 'Value2')
      .click('#entry-edit-properties .q-item--clickable')
  });

  test('Test editing and saving collection', function (browser) {
    browser
      .setInputValue('#entry-edit-title', 'Dataset from frontend test - updated')
      .click('#entry-save-button')
      .expect.url().to.match(/http:\/\/localhost:5000\/datasets\/d-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Dataset from frontend test - updated')
  });

  test('Test deleting dataset', function (browser) {
    browser
      .waitForElementVisible('#entry-about-uuid')
      .click('#entry-info-menu')
      .click('#entry-info-menu-delete')
      .waitForElementVisible('.q-dialog button')
      .click('.q-dialog button:nth-of-type(2)')
      .click('#entry-info-menu')
      .click('#entry-info-menu-delete')
      .waitForElementVisible('.q-dialog button')
      .click('.q-dialog button')
      .assert.urlEquals('http://localhost:5000/datasets')
  });
  
  after(browser => browser.end());
});
