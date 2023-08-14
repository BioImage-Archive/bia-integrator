module.exports = {
    generateNewImage,
    bulkInsertValidateResponse,
    bulkInsertImagesGenerate
};
  

function generateNewImage(requestParams, context, ee, next) { 
    context.vars["img"] = {
        "first": 1,
        "second": "third"
    }

    return next();
}

function bulkInsertValidateResponse(requestParams, response, context, ee, next) {
    let body = JSON.parse(response.body)
    
    for(let item of body.items) {
        if(item.status != 201) {
            return next(Error(`Unexpected bulk insert item status: ${item.status}`));
        }
    }

    return next()
}

function bulkInsertImagesGenerate(requestParams, context, ee, next) {
    const crypto = require('crypto');
    
    // slightly hacky way to parameterize utility functions by passing parameters in a (reserved by us) requestParam named `custom`
    //  @TODO: If we stick to Artillery, set a good convention for this, so that function prototype actually says what variables it expects
    const nImages = requestParams.custom.bulkImageCount;
    
    requestParams.json = [...Array(nImages).keys()].map(_ => ({
        "uuid": crypto.randomUUID(),
        "version": 0,
        "study_uuid": context.vars.study_uuid,
        "name": "image_name_value",
        "original_relpath": "/home/test/image_path_value"
    }));

    return next();
}
