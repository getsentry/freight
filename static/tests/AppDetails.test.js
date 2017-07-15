import React from 'react';
import renderer from 'react-test-renderer';
import AppDetails from '../components/AppDetails.jsx';


//TODO: figure out why snapshots are rendering null.

 test('AppDetails Snapshot', () => {
//   const appList = [{
//     "environments": {
//       "production": {
//         "defaultRef": "master"
//       },
//       "staging": {
//         "defaultRef": "HEAD"
//       },
//     },
//     "id": "1",
//     "app": "freight",
//     "name": "freight",
//     "repository": "https://github.com/getsentry/freight.git"
//   }]
//   const app = {
//     "environments":{
//       "production":{
//         "defaultRef": "master"
//       }
//     },
//     "id": 14,
//     "name": "pipet",
//   };
//   const params = {
//     "app": "pipet"
//   }
//   const task = {
//     'app': {
//       "id": 14,
//       "name": "pipet"
//     },
//     "dateCreated": "2017-07-14T20:41:45.624158Z",
//     "dateFinished": "2017-07-14T20:44:41.312688Z",
//     "dateStarted": "2017-07-14T20:41:47.287309Z",
//     "params": {
//       "app": "pipet"
//     },
//     "duration": 174.03,
//     "environment": "production",
//     "estimatedDuration": 174.03,
//     "id": "6807",
//     "name": "pipet/production#4",
//     "number": 4,
//     "ref": "master",
//     "sha": "6b9071073aea00628cdce320c5cd3fed670860d8",
//     "status": "finished",
//     "user": {
//       "dateCreated": "2017-07-14T20:41:45.624158Z",
//       "id": 15,
//       "name": "james"
//     }
// }
// const apiResponse = [
// {
//   "status": "finished",
//   "app": {
//   "id": "14",
//   "name": "pipet"
//   },
//   "number": 4,
//   "dateCreated": "2017-07-14T20:41:45.624158Z",
//   "user": {
//   "dateCreated": "2015-11-10T19:23:44.100707Z",
//   "id": "15",
//   "name": "eric@getsentry.com"
//   },
//   "duration": 174.03,
//   "dateFinished": "2017-07-14T20:44:41.312688Z",
//   "id": "6807",
//   "estimatedDuration": 174.03,
//   "name": "pipet/production#4",
//   "environment": "production",
//   "sha": "6b9071073aea00628cdce320c5cd3fed670860d8",
//   "dateStarted": "2017-07-14T20:41:47.287309Z",
//   "ref": "master"
//   },
//   {
//   "status": "finished",
//   "app": {
//   "id": "14",
//   "name": "pipet"
//   },
//   "number": 3,
//   "dateCreated": "2017-07-14T17:31:41.878900Z",
//   "user": {
//   "dateCreated": "2015-11-10T19:23:44.100707Z",
//   "id": "15",
//   "name": "eric@getsentry.com"
//   },
//   "duration": 185.46,
//   "dateFinished": "2017-07-14T17:34:48.159300Z",
//   "id": "6802",
//   "estimatedDuration": 185.46,
//   "name": "pipet/production#3",
//   "environment": "production",
//   "sha": "76c3e029251e1eaa9e6f1e14068c89c801b9776d",
//   "dateStarted": "2017-07-14T17:31:42.702537Z",
//   "ref": "master"
//   },
//   {
//   "status": "finished",
//   "app": {
//   "id": "14",
//   "name": "pipet"
//   },
//   "number": 2,
//   "dateCreated": "2017-07-13T23:59:36.162917Z",
//   "user": {
//   "dateCreated": "2015-11-10T19:23:44.100707Z",
//   "id": "15",
//   "name": "eric@getsentry.com"
//   },
//   "duration": 139.26,
//   "dateFinished": "2017-07-14T00:01:56.962379Z",
//   "id": "6798",
//   "estimatedDuration": 139.26,
//   "name": "pipet/production#2",
//   "environment": "production",
//   "sha": "60f4bfb0bd79363cf5d3128f2f6a072019df0a25",
//   "dateStarted": "2017-07-13T23:59:37.707340Z",
//   "ref": "master"
//   },
//   {
//   "status": "finished",
//   "app": {
//   "id": "14",
//   "name": "pipet"
//   },
//   "number": 1,
//   "dateCreated": "2017-07-13T22:09:40.108192Z",
//   "user": {
//   "dateCreated": "2015-04-10T13:58:32.469757Z",
//   "id": "9",
//   "name": "matt@getsentry.com"
//   },
//   "duration": 298.76,
//   "dateFinished": "2017-07-13T22:14:39.664170Z",
//   "id": "6796",
//   "estimatedDuration": 298.76,
//   "name": "pipet/production#1",
//   "environment": "production",
//   "sha": "122704d651045e951f4d0866d33b66f82820c857",
//   "dateStarted": "2017-07-13T22:09:40.905774Z",
//   "ref": "master"
//   }
// ]
//
//   const component = renderer.create(<AppDetails api.request={apiResponse} params={params} tasks={task} appList={appList}/>);
//   expect(component).toMatchSnapshot();
})
