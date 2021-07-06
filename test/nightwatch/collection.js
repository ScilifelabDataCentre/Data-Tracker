describe('Data Tracker - Collections', function() {
  test('Collection Browser - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('#entry-browser-add')

      .setValue('input[type=search]', 'Frontend Test Collection')
      .waitForElementVisible('#entry-c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-c-21c8ecd1-9908-462f-ba84-3ca399074b36', 'Frontend Test Collection')
      .click('#entry-c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .waitForElementVisible('#entry-about-title-text')
      .assert.urlEquals('http://localhost:5000/collections/c-21c8ecd1-9908-462f-ba84-3ca399074b36');
  });

  test('Collection info page - not logged in', function (browser) {
    browser
      .url('http://localhost:5000/collections/c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Frontend Test Collection')
      .assert.containsText('#entry-about-uuid', 'c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.containsText('#entry-about-tags', 'Frontend')
      .assert.containsText('#entry-about-tags', 'Test')
      .assert.containsText('#entry-about-properties .q-chip__content span', 'Type')
      .assert.containsText('#entry-about-properties .q-chip__content', 'Frontend Test Entry')
      .assert.containsText('#entry-about-description', 'A collection added for frontend tests')

      .assert.containsText('#entry-about-datasets-0', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-datasets-0', 'd-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-datasets-1', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-datasets-1', 'd-27cc1144-67bf-45b2-af21-425f9bfc7333')

      .assert.not.elementPresent('#entry-about-related')
      .assert.not.elementPresent('#entry-about-collections')
      .assert.not.elementPresent('#entry-about-authors')
      .assert.not.elementPresent('#entry-about-generators')
      .assert.not.elementPresent('#entry-about-organisation')
      .assert.not.elementPresent('#entry-about-editors')
  }); 

  test('Collection info page - logged in (not editor)', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/generator::frontend')
      .url('http://localhost:5000/collections/c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .waitForElementVisible('#entry-about-title-text')
      .assert.not.elementPresent('#entry-info-menu')
      .assert.not.elementPresent('#entry-about-editors')
  });

  test('Collection info page - logged in (editor)', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/editor::frontend')
      .url('http://localhost:5000/collections/c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .waitForElementVisible('#entry-about-title-text')
      .assert.visible('#entry-info-menu')
      .assert.visible('#entry-about-editors')
  });
  
  test('Add collection', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/generator::frontend')
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/collections/add')

      .setInputValue('#entry-edit-title', 'Collection from frontend test')
      .setInputValue('#entry-edit-description', 'A collection created during a frontend test run')

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

      .assert.not.visible('#entry-edit-datasets .q-table')
      .click('#entry-edit-datasets .q-item--clickable')
      .assert.visible('#entry-edit-datasets .q-table')
      .setValue('#entry-edit-datasets input[type=search]', 'frontend test dataset')
      .pause(300)
      .click('#entry-edit-datasets .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-datasets .q-table tbody tr:nth-of-type(2) div[role=checkbox]')
      .click('#entry-edit-datasets .q-item--clickable')
      .assert.not.visible('#entry-edit-datasets .q-table')    

      .assert.not.visible('#entry-edit-editors .q-table')
      .click('#entry-edit-editors .q-item--clickable')
      .assert.visible('#entry-edit-editors .q-table')
      .setValue('#entry-edit-editors input[type=search]', 'Frontend Editor')
      .pause(300)
      .click('#entry-edit-editors .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-editors .q-item--clickable')
      .assert.not.visible('#entry-edit-editors .q-table')    
  });

  test('Test saving collection', function (browser) {
    browser
      .click('#entry-save-button')
      .expect.url().to.match(/http:\/\/localhost:5000\/collections\/c-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
  });

  test('About collection page - editor', function (browser) {
    browser
      .waitForElementVisible('#entry-about-title-text')
      .assert.not.visible('#entry-save-button')
      .assert.visible('#entry-info-menu')
      .assert.containsText('#entry-about-title-text', 'Collection from frontend test')
      .expect.element('#entry-about-uuid').text.to.match(/c-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .assert.containsText('#entry-about-description', 'A collection created during a frontend test run')
      .assert.containsText('#entry-about-title-text', 'Collection from frontend test')
      .assert.containsText('#entry-about-tags', 'New Tag1')
      .assert.containsText('#entry-about-tags', 'New Tag2')
      .assert.containsText('#entry-about-properties .q-chip span', 'Key1')
      .assert.containsText('#entry-about-properties .q-chip', 'Value1')
      .assert.containsText('#entry-about-properties .q-chip:nth-of-type(2) span', 'Key2')
      .assert.containsText('#entry-about-properties .q-chip:nth-of-type(2)', 'Value2')

      .assert.containsText('#entry-about-datasets-0', 'Frontend Test Dataset')
      .assert.containsText('#entry-about-datasets-0', 'd-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.containsText('#entry-about-datasets-1', 'Frontend Test Dataset 2')
      .assert.containsText('#entry-about-datasets-1', 'd-27cc1144-67bf-45b2-af21-425f9bfc7333')

      .assert.not.elementPresent('#entry-about-order')
      .assert.not.elementPresent('#entry-about-related')
      .assert.not.elementPresent('#entry-about-collections')
    
      .assert.containsText('#entry-about-editors', 'Frontend Editor')
      .assert.not.containsText('#entry-about-editors', 'editor@frontend.dev')
      .click('#entry-about-editors-0 .q-focusable')
      .assert.containsText('#entry-about-editors-0', 'editor@frontend.dev')
      .assert.containsText('#entry-about-editors-0', 'Frontend Test University')
      .assert.containsText('#entry-about-editors-0', 'https://www.example.com/frontend_editor')
      .click('#entry-about-editors-0 .q-focusable')
      .assert.not.containsText('#entry-about-editors-0', 'editor@frontend.dev')
      .click('#entry-about-editors-1 .q-focusable')
      .assert.containsText('#entry-about-editors-1', 'generator@frontend.dev')
      .assert.containsText('#entry-about-editors-1', 'Frontend Test University')
      .assert.containsText('#entry-about-editors-1', 'https://www.example.com/frontend_generator')
      .click('#entry-about-editors-1 .q-focusable')
      .assert.not.containsText('#entry-about-editors-1', 'generator@frontend.dev');
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
      .expect.element('#entry-edit-uuid').text.to.match(/c-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .assert.value('#entry-edit-title', 'Collection from frontend test')
      .assert.value('#entry-edit-description', 'A collection created during a frontend test run')

      .click('#entry-edit-tags .q-item--clickable')
      .assert.containsText('#entry-edit-tags .q-chip', 'New Tag1')
      .assert.containsText('#entry-edit-tags .q-chip:nth-of-type(2)', 'New Tag2')
      .click('#entry-edit-tags .q-item--clickable')

      .click('#entry-edit-properties .q-item--clickable')
      .assert.containsText('#entry-edit-properties .q-chip span', 'Key1')
      .assert.containsText('#entry-edit-properties .q-chip', 'Value1')
      .assert.containsText('#entry-edit-properties .q-chip:nth-of-type(2) span', 'Key2')
      .assert.containsText('#entry-edit-properties .q-chip:nth-of-type(2)', 'Value2')
      .click('#entry-edit-properties .q-item--clickable')

      .click('#entry-edit-datasets .q-item--clickable')
      .pause(300)
      .click('#entry-edit-datasets div[role=checkbox]')
      .assert.containsText('#entry-edit-datasets tbody tr', 'Frontend Test Dataset')
      .assert.containsText('#entry-edit-datasets tbody tr:nth-of-type(2)', 'Frontend Test Dataset 2')
      .click('#entry-edit-datasets .q-item--clickable')

      .click('#entry-edit-editors .q-item--clickable')
      .pause(300)
      .click('#entry-edit-editors div[role=checkbox]')
      .assert.containsText('#entry-edit-editors tbody tr', 'Frontend Editor')
      .assert.containsText('#entry-edit-editors tbody tr:nth-of-type(2)', 'Frontend Generator') // creator added by default
      .click('#entry-edit-editors .q-item--clickable')
  });

  test('Test editing and saving collection', function (browser) {
    browser
      .setInputValue('#entry-edit-title', 'Collection from frontend test - updated')
      .click('#entry-save-button')
      .expect.url().to.match(/http:\/\/localhost:5000\/collections\/c-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Collection from frontend test - updated')
  });
  
  test('Test deleting collection', function (browser) {
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
      .assert.urlEquals('http://localhost:5000/collections/')
  });

  after(browser => browser.end());
});
