var Directory, Express, File, HostFileSystem, ServerError, Url, router;

Express = require('express');

Url = require('url');

Directory = require('../directory.js');

File = require('../file.js');

HostFileSystem = require('../host-fs.js');

ServerError = require_harrogate_module('/shared/scripts/server-error.js');

// the fs router
router = Express.Router();

// '/' is relative to <manifest>.web_api.fs.uri
router.use('/', function(request, response, next) {
  // Create the fs resource
  HostFileSystem.open({
    uri: Url.parse(request.originalUrl, true).pathname
  }).then(function(value) {
    // store it and continue
    request.fs_resource = value;
    next();
  })["catch"](function(error) {
    // could not create the fs resource (wrong path)
    next(error);
  }).done();
});

router.get('/*', function(request, response, next) {
  var fs_path, response_mode;
  // the the FS path
  fs_path = request.fs_resource.path;

  // is the raw file or the JSON object requested?
  response_mode = Url.parse(request.url, true).query['mode'];
  if ((response_mode != null) && response_mode === 'raw') {
    response.download(fs_path);
  } else {
    request.fs_resource.get_representation().then(function(representation) {
      response.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      response.setHeader('Pragma', 'no-cache');
      response.setHeader('Expires', '0');
      response.writeHead(200, {
        'Content-Type': 'application/json'
      });
      response.end("" + (JSON.stringify(representation)), 'utf8');
    })["catch"](function(error) {
      next(error);
    }).done();
  }
});

router.post('/*', function(request, response, next) {
  var content, encoding, ref, resource_promise;

  // We only support application/json
  if (!/application\/json/i.test(request.headers['content-type'])) {
    next(new ServerError(415, 'Only content-type application/json supported'));
    return;
  }

  // Check if the uri points to a directory
  if (!(request.fs_resource instanceof Directory)) {
    next(new ServerError(400, request.fs_resource.path + ' is not a directory'));
    return;
  }

  // Validate the name
  if (request.body.name == null) {
    next(new ServerError(422, 'Parameter \'name\' missing'));
    return;
  }

  // Validate the type
  if (request.body.type == null) {
    next(new ServerError(422, 'Parameter \'type\' missing'));
    return;
  }

  if ((ref = request.body.type) !== 'file' && ref !== 'directory') {
    next(new ServerError(422, 'Invalid value for parameter \'type\''));
    return;
  }

  if (request.body.type === 'directory') {
    resource_promise = request.fs_resource.create_subdirectory(request.body.name);
  } else {
    // request.body.type is 'file'
    encoding = request.body.encoding != null ? request.body.encoding : 'ascii';
    content = request.body.content != null ? new Buffer(request.body.content, 'base64').toString(encoding) : '';
    resource_promise = request.fs_resource.create_file(request.body.name, content, encoding);
  }

  resource_promise.then(function(resource) {
    response.writeHead(201, {
      'Location': "" + resource.uri
    });
    response.end();
  })["catch"](function(error) {
    next(error);
  }).done();
});

router.put('/*', function(request, response, next) {
  var content, encoding;

  if (!/application\/json/i.test(request.headers['content-type'])) {
    next(new ServerError(415, 'Only content-type application/json supported'));
    return;
  }

  if (!(request.fs_resource instanceof File)) {
    next(new ServerError(400, request.fs_resource.path + ' is not a file'));
    return;
  }

  encoding = request.body.encoding != null ? request.body.encoding : 'ascii';
  content = request.body.content != null ? Buffer.from(request.body.content, 'base64').toString(encoding) : '';

  request.fs_resource.write(content, encoding).then(function() {
    response.writeHead(204);
    response.end();
  }).catch(function(error) {
    next(error);
  }).done();
});


router["delete"]('/*', function(request, response) {
  // delete the fs resource
  request.fs_resource.remove().then(function() {
    response.writeHead(204);
    response.end();
  })["catch"](function(err) {
    if (err.code === 'ENOTEMPTY') {
      next(new ServerError(403, request.fs_resource.name + ' is not empty'));
      return;
    }
    if (err.code === 'ENOENT') {
      next(new ServerError(404, 'No such file or directory'));
      return;
    }
    // the file exists but we cannot delete it...
    next(new ServerError(403, 'Unable to delete ' + request.fs_resource.name));
  }).done();
});

// export the router object
module.exports = router;
