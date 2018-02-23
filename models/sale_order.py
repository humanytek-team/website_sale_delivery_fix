from openerp import api, fields, models
from openerp import SUPERUSER_ID
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_delivery_methods(self, cr, uid, order, context=None):
        # even faster
        # SELECT id FROM delivery_carrier INNER JOIN delivery_carrier_country_rel ON delivery_carrier_country_rel.carrier_id = delivery_carrier.id AND delivery_carrier_country_rel.country_id = + aux_country_id  INNER JOIN delivery_carrier_state_rel ON delivery_carrier_state_rel.carrier_id=delivery_carrier.id AND delivery_carrier_state_rel.state_id = + aux_state_id  WHERE zip_from >= aux_zip + AND zip_to <= aux_zip
        carrier_obj = self.pool.get('delivery.carrier')
        carrier_ids = carrier_obj.search(
            cr, SUPERUSER_ID, [('website_published', '=', True),
                               ('zip_from', '<=', order.partner_shipping_id.zip),
                               ('zip_to', '>=', order.partner_shipping_id.zip), ], context=context)

        available_carrier_ids = []

        new_context = dict(context, order_id=order.id)
        for carrier in carrier_ids:
            try:
                available = carrier_obj.read(cr, SUPERUSER_ID, [carrier], fields=[
                                             'available'], context=new_context)[0]['available']
                if available:
                    available_carrier_ids = available_carrier_ids + [carrier]
            except ValidationError as e:
                pass
        return available_carrier_ids
