<template>
<q-page padding>
  <h2>User Guide </h2>
  <q-card class="q-my-md">
    <q-card-section>
      The SciLifeLab Data Tracker tracks data generated from the facilities in SciLifeLab. It only contains information about the generated data, that is the metadata, not the data itself.
    </q-card-section>
  </q-card>
  <q-card class="q-my-md">
    <q-card-section>
      <h3>Data Types</h3>

      The data tracker is based on three data types: <span class="text-italic">orders</span>, <span class="text-italic">datasets</span>, and <span class="text-italic">collections</span>. Only <span class="text-italic">datasets</span> and <span class="text-italic">collections</span> are visible to most users.
    </q-card-section>

    <q-card-section>
      <h4>Orders</h4>
      <ul>
        <li>An order is intended to correspond to an order made to a facility</li>
        <li>Orders are intended as a way to group data releases (datasets) that originate from the same ordering body together</li>
        <li>Orders are considered to be "internal" data, and will thus only be visible to the users listed as `editors` for the order</li>
        <li>For more information, e.g. what fields are available, see the <a class="text-link" href="https://scilifelabdatacentre.github.io/Data-Tracker/data_structure.html#order">documentation</a></li>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Datasets</h4>
      <ul>
        <li>A dataset is a data released from an order, i.e. one dataset belongs to <span class="text-italic">one</span> order</li>
        <li>As the dataset is connected to one order, it will share the same authors, data generators, and organisation (and internally, editors as well)</li>
        <li>For more information, e.g. what fields are available, see the <a class="text-link" href="https://scilifelabdatacentre.github.io/Data-Tracker/data_structure.html#dataset">documentation</a></li>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Collections</h4>
      <ul>
        <li>Collections are intended to link together datasets from different orders, e.g. if the same project has received data from multiple facilities</li>
        <li>Any logged in user can associate any dataset with the collections they manage</li>
        <li>For more information, e.g. what fields are available, see the <a class="text-link" href="https://scilifelabdatacentre.github.io/Data-Tracker/data_structure.html#collection">documentation</a></li>
      </ul>
    </q-card-section>
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <h3>Using the website</h3>
    </q-card-section>

    <q-card-section>
      <ul>
        <li>The Data Tracker website can be used to list orders, datasets, and collections, as well as managing users</li>
        <li>Before logging in, you can explore all available datasets and collections</li>
        <li>You can <router-link class="text-link" :to="{'name': 'Login'}">log in</router-link> to access more functionality</li>
        <ul>
          <li>You can log in by using OpenID Connect (currently supporting scilifelab.se logins via Google) or your authentication ID together with an API key</li>
          <li>The first time you log in, you should use OpenID, as the other option requires an existing account</li>
        </ul>
        <li>Logged in users can set some information about themselves, e.g. affiliation and contact information, by choosing <router-link class="text-link" :to="{name: 'About Current User'}">Current User</router-link> in the menu</li>
        <li>All logged in users can create collections.</li>
        <li>Users may also get extended permissions to e.g. modify any order/dataset/collection or user</li>
        <ul>
          <li>The available permissions are listed in the <a class="text-link" href="https://scilifelabdatacentre.github.io/Data-Tracker/implementation.html#current-units">documentation</a></li>
        </ul>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Orders</h4>
      <ul>
        <li>In order to work with orders, the user must have the ORDERS permission</li>
        <li>A list of orders where the current user has editing permissions can be found in the <router-link class="text-link" :to="{name: 'Order Browser'}">Order Browser</router-link> </li>
        <ul>
          <li>A user with the permission DATA_MANAGEMENT will get a list of all orders</li>
        </ul>
        <li>Create a new order by the clicking "+" at the top of the browser, or directly on <router-link class="text-link" :to="{name: 'Order New'}">this page</router-link></li>
        <li>When you open an order entry, there will be an option menu on top with three choices:</li>
        <ul>
          <li>Edit &mdash; open the edit mode for the entry, giving an edit and a preview tab as well as buttons for cancel and save</li>
          <li>Delete &mdash; delete the entry</li>
          <li>Show History &mdash; show a list of changes to the order, including when the changes were made and by whom</li>
        </ul>
        <li>Editing an order:</li>
        <ul>
          <li>The preview tab shows how the order will be presented with the edited data</li>
          <li>Title may not be empty</li>
          <li>Desciption will be rendered as markdown</li>
          <li>Authors, generators, organisation, and editors are selected from lists of all users</li>
          <ul>
            <li>New users are added in the <router-link class="text-link" :to="{name: 'User Manager'}">User Manager</router-link> or by clicking the add user </li>
            <li>If no editors are selected, the current user will become the sole editor</li>
          </ul>
        </ul>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Datasets</h4>
      <ul>
        <li>In order to work with datasets, the user must have the ORDERS permission</li>
        <li>A list of all datasets can be found in the <router-link class="text-link" :to="{name: 'Dataset Browser'}">Dataset Browser</router-link> </li>
        <li>Create a new dataset by the clicking "+" at the top of the browser, or directly on <router-link class="text-link" :to="{name: 'Dataset New'}">this page</router-link></li>
        <ul>
          <li>When creating a dataset, start by selecting an order to connect the new dataset to in the order list</li>
          <ul>
            <li> To be able add datasets, you need to have an order </li>
            <li>After selecting an order, the title, description, tags etc will be copied to the dataset entry</li>
          </ul>
        </ul>
        <li>When you open a dataset entry, there will be an option menu on top with three choices:</li>
        <ul>
          <li>Edit &mdash; open the edit mode for the entry, giving an edit and a preview tab as well as buttons for cancel and save</li>
          <li>Delete &mdash; delete the entry</li>
          <li>Show History &mdash; show a list of changes to the order, including when the changes were made and by whom</li>
        </ul>
        <li>Editing a dataset:</li>
        <ul>
          <li>The preview tab shows how the order will be presented with the edited data</li>
          <li>Title field cannot be empty</li>
          <li>Desciption will be rendered as markdown</li>
          <li>Authors, generators, organisation, and editors are inherited from the order and cannot be set for the individual dataset</li>
        </ul>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Collections</h4>
      <ul>
        <li>A list of all collections can be found in the <router-link class="text-link" :to="{name: 'Collection Browser'}">Collection Browser</router-link> </li>
        <li>Create a new collection by the clicking "+" at the top of the browser, or directly on <router-link class="text-link" :to="{name: 'Collection New'}">this page</router-link></li>
        <li>When you open a collection entry, there will be an option menu on top with three choices:</li>
        <ul>
          <li>Edit &mdash; open the edit mode for the entry, giving an edit and a preview tab as well as buttons for cancel and save</li>
          <li>Delete &mdash; delete the entry</li>
          <li>Show History &mdash; show a list of changes to the order, including when the changes were made and by whom</li>
        </ul>
        <li>Editing a collection:</li>
        <ul>
          <li>The preview tab shows how the order will be presented with the edited data</li>
          <li>Title may not be empty</li>
          <li>Desciption will be rendered as markdown</li>
          <li>Editors are selected from lists of all users</li>
          <ul>
            <li>If no editors are selected, the current user will become the sole editor</li>
          </ul>
        </ul>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Users</h4>
      <ul>
        <li>Accessing user information requires USER_ADD, USER_SEARCH, and/or USER_MANAGEMENT depending on the operation
        <li>A list of all users is available in the <router-link class="text-link" :to="{name: 'User Manager'}">User Manager</router-link></li>
        <ul>
          <li>New users can be created by clicking "+"</li>
          <li>Click on the pen for a user to access more information (requires USER_MANAGEMENT)
          <li>Email must be provided for all added users</li>
          <li>Only users with USER_MANAGEMENT can set permissions</li>
        </ul>
      </ul>
    </q-card-section>    
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <h3>Working with the API</h3>
      <ul>
        <li>The full API is listed in the <a class="text-link" href="https://scilifelabdatacentre.github.io/Data-Tracker/api.html">API documentation</a></li>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Generating and using an API key</h4>
      <ul>
        <li>API keys can be generated on the <router-link class="text-link" :to="{name: 'About Current User'}">Current User</router-link> page</li>
        <li>API keys can also be generated in the API by making a POST to /api/v1/user/me/apikey or /api/v1/user/"uuid"/apikey</li>
        <li>In order to use your API keys with your requests by setting the headers X-API-User and X-API-Key with one of your authentication IDs and your API key</li>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Adding entries</h4>
      <ul>
        <li>Entries are added by making POST requests to the data type in the API</li>
        <li>The general fields for a data type is available at /data type/structure</li>
      </ul>
    </q-card-section>

    <q-card-section>
      <h5>Order</h5>
      <ul>
        <li>POST to /api/v1/order/</li>
        <li>Include a JSON payload</li>
      </ul>
      <q-markdown>
```
{
  "authors": ["ee351748-a1d0-411c-ba85-0f0e47707c4f"], 
  "description": "*markdown* formatted text", 
  "editors": ["ee351748-a1d0-411c-ba85-0f0e47707c4f"], 
  "generators": ["ee351748-a1d0-411c-ba85-0f0e47707c4f"], 
  "organisation": "ee351748-a1d0-411c-ba85-0f0e47707c4f", 
  "tags": ["tag1", "tag2"], 
  "title": "Title of the order"
}
```
      </q-markdown>
    </q-card-section>

    <q-card-section>
      <h5>Dataset</h5>
      <ul>
        <li>POST to /api/v1/dataset/</li>
        <li>Include a JSON payload</li>
      </ul>
      <q-markdown>
```
{
  "order": "ee351748-a1d0-411c-ba85-0f0e47707c4f",
  "description": "*markdown* formatted text", 
  "tags": ["tag1", "tag2"], 
  "title": "Title of the dataset"
}
```
      </q-markdown>
    </q-card-section>

    <q-card-section>
      <h5>Collection</h5>
      <ul>
        <li>POST to /api/v1/collection/</li>
        <li>Include a JSON payload</li>
      </ul>
      <q-markdown>
```
{
  "description": "*markdown* formatted text",
  "datasets": ["ee351748-a1d0-411c-ba85-0f0e47707c4f", "abcdefgh-a1d0-411c-abcd-0f0e47707c4f"]
  "editors": ["ee351748-a1d0-411c-ba85-0f0e47707c4f"]
  "tags": ["tag1", "tag2"], 
  "title": "Title of the collection"
}
```
      </q-markdown>
    </q-card-section>

    <q-card-section>
      <h5>User</h5>
      <ul>
        <li>POST to /api/v1/user/</li>
        <li>Include a JSON payload</li>
      </ul>
      <q-markdown>
```
{
    "affiliation": "UU", 
    "contact": "Letter to xy or email to email@example.com", 
    "email": "email@example.com", 
    "name": "First Last", 
    "orcid": "0000-0001-2345-6789", 
    "permissions": ['ORDERS'], 
    "url": "https://www.example.com"
}
```
      </q-markdown>
    </q-card-section>

    <q-card-section>
      <h4>Modifying entries</h4>
      <ul>
        <li>Entries are modified by making PATCH requests to the uuid in the API (/data type/uuid/)</li>
      </ul>
    </q-card-section>

    <q-card-section>
      <h4>Deleting entries</h4>
      <ul>
        <li>Entries are deleted by making DELETE requests to the uuid in the API (/data type/uuid/)</li>
      </ul>
    </q-card-section>
    
  </q-card>
</q-page>
</template>

<script>
export default {
  name: 'UserGuide',
}
</script>
