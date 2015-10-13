import pytest
import json

PUT_DATA = {
    "triggers": [
        {
            "id": 76,
            "properties": {
                "elementInstanceId": "${notpt.dynamics.id}",
                "api": "/hubs/crm/salesorder",
                "method": "POST"
            },
            "type": "elementRequest",
            "onSuccess": [
                "getDynamicsOrderId"
            ]
        }
    ],
    "steps": [
        {
            "mimeType": "application/javascript",
            "body": "return steps.lookupQBCustomer.exists;\n",
            "name": "buildNewCustomer",
            "onFailure": [
                "prepareCreateQBCustomer"
            ],
            "onSuccess": [
                "getDynamicsProductId"
            ],
            "type": "filter"
        },
        {
            "mimeType": "application/javascript",
            "body": "var productInfo = steps.getProductName.numProducts;\nvar products = steps.lookupQBProduct.response.body;\n\nreturn productInfo == products.size();\n",
            "name": "checkProducts",
            "onFailure": [],
            "onSuccess": [
                "getPaymentTermsId"
            ],
            "type": "filter"
        },
        {
            "mimeType": "application/javascript",
            "body": "var dynamicsOrder = steps.getDynamicsOrder.response.body.attributes;\nvar dynamicsOrderDetail = steps.getDynamicsOrderDetail.response.body[0].attributes;\nvar qbCustomer = steps.lookupQBCustomer;\nvar custListId = qbCustomer.listId;\nvar custName = qbCustomer.accountName;\nvar qbProduct = steps.lookupQBProduct.response.body[0];\nvar dueDate = steps.getDueDate.dueDate;\n\nvar salesTaxRef = qbProduct.SalesTaxCodeRef;\n\nvar orderLines = [];\n\n// Use created customer if qbCustomer is null...\nif (!qbCustomer.exists) {\n    qbCustomer = steps.createQBCustomer.response.body;\n    custListId = qbCustomer.ListID;\n    custName = qbCustomer.FullName;\n}\n\nlogger.debug('customer: ' + JSON.stringify(qbCustomer));\n\nvar quickbooksOrder = {\n    BillAddress: {\n        Addr1: dynamicsOrder.billto_name,\n        Addr2: dynamicsOrder.billto_line1,\n        City: dynamicsOrder.billto_city,\n        State: dynamicsOrder.billto_stateorprovince,\n        PostalCode: dynamicsOrder.billto_postalcode\n    },\n    ShipAddress: {\n        Addr1: dynamicsOrder.shipto_name,\n        Addr2: dynamicsOrder.shipto_line1,\n        City: dynamicsOrder.shipto_city,\n        State: dynamicsOrder.shipto_stateorprovince,\n        PostalCode: dynamicsOrder.shipto_postalcode\n    },\n    ClassRef: {\n        ListID: '80000008-1576428924',\n        FullName: 'Passtime USA'\n    },\n    CustomerRef: {\n        ListID: custListId,\n        FullName: custName\n    },\n    nje_salesperson: dynamicsOrder.nxt_rep,\n    SalesOrderLine: JSON.stringify([\n        {\n            ItemRef: {\n                ListID: qbProduct.ListID\n            },\n            Desc: dynamicsOrderDetail.productdescription,\n            Quantity: dynamicsOrderDetail.quantity,\n            Rate: qbProduct.PurchaseCost,\n            SalesTaxCodeRef: {\n                ListID: salesTaxRef.ListID,\n                FullName: salesTaxRef.FullName\n            }\n        }\n    ]),\n    DueDate: dueDate\n};\n\nlogger.debug('quickbooksOrder: ' + JSON.stringify(quickbooksOrder));\n\nreturn quickbooksOrder;\n",
            "type": "script",
            "onSuccess": [
                "createOrUpdate"
            ],
            "name": "convertToQuickbooksOrder"
        },
        {
            "mimeType": "application/javascript",
            "body": "",
            "type": "script",
            "onSuccess": [
                "sendErrorNotice"
            ],
            "name": "createErrorNotice"
        },
        {
            "mimeType": "application/javascript",
            "body": "logger.debug('quickbooksOrderId: ' + steps.getDynamicsOrder.quickbooksId);\nreturn steps.getDynamicsOrder.quickbooksId == null;\n",
            "name": "createOrUpdate",
            "onFailure": [
                "getQuickbooksOrder"
            ],
            "onSuccess": [
                "createQuickbooksOrder"
            ],
            "type": "filter"
        },
        {
            "mimeType": "application/javascript",
            "body": "${steps.prepareCreateQBCustomer}",
            "name": "createQBCustomer",
            "onSuccess": [
                "getDynamicsProductId"
            ],
            "api": "/hubs/finance/customers",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "POST"
        },
        {
            "mimeType": "application/javascript",
            "body": "${steps.convertToQuickbooksOrder}",
            "name": "createQuickbooksOrder",
            "onSuccess": [
                "getNewQuickbooksSalesOrderId"
            ],
            "api": "/hubs/finance/sales-orders",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "POST"
        },
        {
            "mimeType": "application/javascript",
            "body": "var paymentTermName = steps.lookupQBPaymentTerm.response.body[0];\nvar dueDate = new Date();\n\nif (paymentTermName.equals('Net 30')) {\n    dueDate += 30;\n} else if (paymentTermName.equals('Net 15')) {\n    dueDate += 15;\n}\n\nvar result = {\n    dueDate: dueDate.getFullYear().toString() + '-' + dueDate.getMonth() + '-' + dueDate.getDay()\n};\n\nlogger.debug('due date: ' + result.dueDate);\n\nreturn result;\n",
            "type": "script",
            "onSuccess": [
                "convertToQuickbooksOrder"
            ],
            "name": "getDueDate"
        },
        {
            "mimeType": "application/javascript",
            "name": "getDynamicsCustomer",
            "onSuccess": [
                "parseQuickbooksCustomerId"
            ],
            "api": "/hubs/crm/accounts/{id}",
            "path": "${steps.getDynamicsCustomerId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "var order = steps.getDynamicsOrder.response.body.attributes;\nlogger.debug('order: ' + order);\n\nvar update = {\n    id: order.customerid  // This is the real value...\n};\n\nlogger.debug('customerid: ' + update.id);\n\nreturn update;\n",
            "type": "script",
            "onSuccess": [
                "getDynamicsCustomer"
            ],
            "name": "getDynamicsCustomerId"
        },
        {
            "mimeType": "application/javascript",
            "name": "getDynamicsOrder",
            "onSuccess": [
                "getDynamicsOrderDetail"
            ],
            "api": "/hubs/crm/salesorder/{id}",
            "path": "${steps.getDynamicsOrderId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "name": "getDynamicsOrderDetail",
            "onSuccess": [
                "getDynamicsCustomerId"
            ],
            "api": "/hubs/crm/salesorderdetail?where=salesorderid%3D'{id}'",
            "path": "${steps.getDynamicsOrderId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "//var order = trigger.response.body;\n//logger.debug('order: ' + order);\n// Where will the order number come from when there's no\n\nvar update = {\n    //id: order.id This is the real value\n    id: '8099ddb5-b758-e511-8101-d89d672cdd98'\n    //id: '2f4696a5-3d5b-e511-8101-d89d672cdd98'\n};\n\nreturn update;\n",
            "type": "script",
            "onSuccess": [
                "getDynamicsOrder"
            ],
            "name": "getDynamicsOrderId"
        },
        {
            "mimeType": "application/javascript",
            "name": "getDynamicsProduct",
            "onSuccess": [
                "getProductName"
            ],
            "api": "/hubs/crm/products?where=productid%20in%20{id}",
            "path": "${steps.getDynamicsProductId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "var orderDetail = steps.getDynamicsOrderDetail.response.body;\nvar detailProductId;\nvar idString = '(' + '\\'' + orderDetail[0].attributes.productid + '\\'';\n\nfor (var k = 1; k < orderDetail.size(); k++) {\n    detailProductId = orderDetail[k].attributes.productid;\n    logger.debug('orderDetail item: ' + detailProductId);\n    idString = idString + ',%20\\'' + detailProductId + '\\''\n}\n\nvar productId = {\n    id: idString + ')',\n    quantity: orderDetail.quantity\n};\n\nreturn productId;\n",
            "type": "script",
            "onSuccess": [
                "getDynamicsProduct"
            ],
            "name": "getDynamicsProductId"
        },
        {
            "mimeType": "application/javascript",
            "name": "getDynamicsSalesRep",
            "onSuccess": [
                "getDueDate"
            ],
            "api": "/hubs/crm/nje_salesperson/{id}",
            "path": "${steps.getDynamicsSalesRepId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "var order = steps.getDynamicsOrder.response.body.attributes;\nlogger.debug('order: ' + order);\n\nvar salesRepId = {\n    //id: order.nje_commissionablesalesrepid  This is the real value\n    id: '77cc1b47-4551-de11-b48a-00237d653ed0'\n};\n\nreturn salesRepId;\n",
            "type": "script",
            "onSuccess": [
                "getDynamicsSalesRep"
            ],
            "name": "getDynamicsSalesRepId"
        },
        {
            "mimeType": "application/javascript",
            "body": "var quickbooksSalesOrder = steps.createQuickbooksOrder.response.body;\nvar quickbooksOrderId = quickbooksSalesOrder.id;\n\nvar update = {quickbooksId: quickbooksOrderId};\nprint(JSON.stringify(update));\nreturn update;\n",
            "type": "script",
            "onSuccess": [
                "prepareUpdateDynamicsOrder"
            ],
            "name": "getNewQuickbooksSalesOrderId"
        },
        {
            "mimeType": "application/javascript",
            "name": "getPaymentTerm",
            "onSuccess": [
                "getPaymentTermName"
            ],
            "api": "/hubs/crm/nje_paymentterm/{id}",
            "path": "${steps.getPaymentTermsId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "var dynamicsPaymentTerm = steps.getPaymentTerm.response.body.attributes;\nvar paymentTermName = dynamicsPaymentTerm.nje_name;\nvar translatedName;\n\nif (paymentTermName === 'Due Upon Receipt') {\n    translatedName = 'Due%20on%20Receipt';\n} else if (paymentTermName = 'NET 15') {\n    translatedName = 'Net%2015';\n} else if (paymentTermName = 'NET 30') {\n    translatedName = 'Net%2030';\n} else {\n    translatedName = null;\n}\n\nvar result = {\n    id: translatedName\n};\n\nlogger.debug('payment term name: ' + result);\n\nreturn result;\n",
            "type": "script",
            "onSuccess": [
                "lookupQBPaymentTerm"
            ],
            "name": "getPaymentTermName"
        },
        {
            "mimeType": "application/javascript",
            "body": "var order = steps.getDynamicsOrder.response.body.attributes;\nlogger.debug('order: ' + order);\n\nvar termsId = {\n    id: order.nje_paymenttermsid\n};\n\nreturn termsId;\n",
            "type": "script",
            "onSuccess": [
                "getPaymentTerm"
            ],
            "name": "getPaymentTermsId"
        },
        {
            "mimeType": "application/javascript",
            "body": "var dynamicsProductList = steps.getDynamicsProduct.response.body;\nvar productNames = '(\\'' + encodeURIComponent(dynamicsProductList[0].attributes.name) + '\\'';\n\nfor (var k = 1; k < dynamicsProductList.size(); k++) {\n    productNames = productNames + ',%20\\'' + encodeURIComponent(dynamicsProductList[k].attributes.name) + '\\'';\n}\n\nproductNames = productNames + ')';\n\nvar result = {\n    id: productNames,\n    numProducts: dynamicsProductList.size()\n};\n\nlogger.debug('product names: ' + JSON.stringify(result));\n\nreturn result;\n",
            "type": "script",
            "onSuccess": [
                "lookupQBProduct"
            ],
            "name": "getProductName"
        },
        {
            "mimeType": "application/javascript",
            "name": "getQuickbooksOrder",
            "onSuccess": [],
            "api": "/hubs/finance/purchase-order/{id}",
            "path": "${steps.getNewQuickbooksSalesOrderId}",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "var customerList = steps.searchQuickbooksCustomers.response.body;\nvar acctNumber = steps.parseQuickbooksCustomerId.id;\nvar exists = false;\nvar accountNumber = null;\nvar accountName = null;\nvar account;\n\nfor (var k = 0; k < customerList.size(); k++) {\n    account = customerList[k];\n\n    logger.debug('account number: ' + account.AccountNumber);\n    logger.debug('acctNumber: ' + acctNumber);\n\n    if (account.AccountNumber != null && account.AccountNumber.equals(acctNumber)) {\n        exists = true;\n        accountNumber = account.AccountNumber;\n        accountName = account.FullName;\n        break;\n    }\n}\n\nlogger.debug('exists: ' + exists);\nlogger.debug('accountNumber: ' + accountNumber);\nlogger.debug('name: ' + accountName);\n\nvar result = {\n    exists: exists,\n    accountNumber: accountNumber,\n    accountName: accountName\n};\n\nreturn result;\n",
            "type": "script",
            "onSuccess": [
                "buildNewCustomer"
            ],
            "name": "lookupQBCustomer"
        },
        {
            "mimeType": "application/javascript",
            "name": "lookupQBPaymentTerm",
            "onSuccess": [
                "getDynamicsSalesRepId"
            ],
            "api": "/hubs/finance/credit-terms?where=Name%3D'{id}'",
            "path": "${steps.getPaymentTermName}",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "name": "lookupQBProduct",
            "onSuccess": [
                "checkProducts"
            ],
            "api": "/hubs/finance/products?where=Name%20in%20{id}",
            "path": "${steps.getProductName}",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "var dynamicsAccount = steps.getDynamicsCustomer.response.body.attributes;\nvar acctNumber = dynamicsAccount.nje_gpaccountnumber;\nvar parsedNumber = acctNumber.replace(/^0+/, '');\n\nvar result = {\n    id: parsedNumber  // This is the real value\n};\n\nlogger.debug('parsed number: ' + result);\n\nreturn result;\n",
            "type": "script",
            "onSuccess": [
                "parseQuickbooksCustomerName"
            ],
            "name": "parseQuickbooksCustomerId"
        },
        {
            "mimeType": "application/javascript",
            "body": "var dynamicsAccount = steps.getDynamicsCustomer.response.body.attributes;\nvar acctName = dynamicsAccount.name;\nvar parsedName = acctName.substring(0, 2);\n\nvar result = {\n    id: parsedName + '%25'\n};\n\nlogger.debug('parsed name: ' + result);\n\nreturn result;\n",
            "type": "script",
            "onSuccess": [
                "searchQuickbooksCustomers"
            ],
            "name": "parseQuickbooksCustomerName"
        },
        {
            "mimeType": "application/javascript",
            "body": "var dynamicsCustomer = steps.getDynamicsCustomer.response.body.attributes;\n\nvar quickbooksCustomer = {\n    Name: dynamicsCustomer.name,\n    Email: dynamicsCustomer.emailaddress1,\n    Phone: dynamicsCustomer.telephone1,\n    AccountNumber: steps.parseQuickbooksCustomerId.id\n};\n\nlogger.debug('quickbooksCustomer: ' + JSON.stringify(quickbooksCustomer));\n\nreturn quickbooksCustomer;\n",
            "type": "script",
            "onSuccess": [
                "createQBCustomer"
            ],
            "name": "prepareCreateQBCustomer"
        },
        {
            "mimeType": "application/javascript",
            "body": "var qbOrder = steps.createQuickbooksOrder.response.body;\n\nvar dynamicsOrder = {\n    attributes: {\n        new_quickbooksid: qbOrder.id           // This name is tentative (Dynamics insists on the \"new_\" part)\n    }\n};\n\nlogger.debug('dynamicsOrder: ' + JSON.stringify(dynamicsOrder));\n\nreturn dynamicsOrder;\n",
            "type": "script",
            "onSuccess": [
                "updateDynamicsSalesOrder"
            ],
            "name": "prepareUpdateDynamicsOrder"
        },
        {
            "mimeType": "application/javascript",
            "body": "${steps.convertToQuickbooksOrder}",
            "name": "retrieveExecutionTrace",
            "onSuccess": [
                "createErrorNotice"
            ],
            "api": "/hubs/finance/sales-orders",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "POST"
        },
        {
            "mimeType": "application/javascript",
            "name": "retrieveSalesRep",
            "onSuccess": [
                "retrievePaymentTerm"
            ],
            "api": "/hubs/crm/nje_salesperson/{id}",
            "path": "${steps.getDynamicsOrder.response.body.attributes.nje_commissionablesalesrepid}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "name": "searchQuickbooksCustomers",
            "onSuccess": [
                "lookupQBCustomer"
            ],
            "api": "/hubs/finance/customers?where=Name%20like%20'{id}'",
            "path": "${steps.parseQuickbooksCustomerName}",
            "elementInstanceId": "${quickbooks.id}",
            "type": "elementRequest",
            "method": "GET"
        },
        {
            "mimeType": "application/javascript",
            "body": "${steps.prepareUpdateDynamicsOrder}",
            "name": "updateDynamicsSalesOrder",
            "onFailure": [
                "sendFailureNotice"
            ],
            "onSuccess": [],
            "api": "/hubs/crm/salesorder/{id}",
            "path": "${steps.getDynamicsOrderId}",
            "elementInstanceId": "${dynamics.id}",
            "type": "elementRequest",
            "method": "PATCH"
        }
    ],
    "configuration": [
        {
            "name": "quickbooksInstance",
            "description": "The quickbooks element instance",
            "type": "elementInstance",
            "key": "quickbooks.id"
        },
        {
            "name": "dynamicsInstance",
            "description": "The dynamics crm element instance",
            "type": "elementInstance",
            "key": "dynamics.id"
        },
        {
            "name": "otherDynamicsInstance",
            "description": "The not-Passtime dynamics crm element instance",
            "type": "elementInstance",
            "key": "notpt.dynamics.id"
        }
    ],
    "name": "dynamicsToQuickbooksSalesOrder",
    "description": "Create or Update sales order in QB based on Dynamics"
}

def test_put_workflow(WorkFlowAPI):

    data = json.dumps(PUT_DATA)
    WorkFlowAPI.send_request("put", WorkFlowAPI.workflow_id_path.format(workflow_id=275), data=data)
    WorkFlowAPI.print_my_last()
    assert False

def test_get_executions(WorkFlowAPI):
    workflow_id_instances_id_executions_path
