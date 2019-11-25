from frappe import _

def get_data():
   return {
      'fieldname': 'sales_report_group',
      'transactions': [
         {
            'label': _('Items'),
            'items': ['Item']
         }
      ]
   }
