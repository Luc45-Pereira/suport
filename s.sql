SELECT
  DISTINCT shipping.id AS "id_pedido",
  DATE_FORMAT(o.date_created, '%%d/%%m/%%Y %%H:%%i:%%s') AS "data de criação do pedido",
  (SELECT DATE_FORMAT(MAX(pay.date_approved), '%%d/%%m/%%Y %%H:%%i:%%s')
    FROM cs_trading_order_shipping_payment pay
    WHERE pay.shipping_id = shipping.id
  ) AS "data de aprovação do pagamento",
  shipping.shipping_number AS "nº transação",
  o.order_type AS canal,
  s.id AS "id lojista",
  s.name AS "nome lojista",
  c.id AS "id grupo",
  c.name AS "nome grupo",
  GROUP_CONCAT(
    COALESCE(cp.mpn, kit.mpn) SEPARATOR '|'
  ) AS "produtos",
  (CASE
    WHEN shipping.state = 'approved' THEN 'aprovado'
    WHEN shipping.state = 'invoiced' THEN 'faturado'
    WHEN shipping.state = 'shipped' THEN 'enviado'
    WHEN shipping.state = 'delivered' THEN 'entregue'
    WHEN shipping.state = 'closed' THEN 'fechado'
    WHEN shipping.state = 'preinvoiced' THEN 'pre-faturado'
    WHEN shipping.state = 'preapproved' THEN 'pre-aprovado'
  END) AS status,
  shipping.total_payments_amount AS total,
  shipping.total_payments_fee_amount AS "total descontos",
  shipping.total_payments_net_amount AS "total liquido",
  o.order_type AS canal,
  (
    CASE
      WHEN p.status != 'approved' THEN 'sim'
      WHEN p.status = 'approved' THEN 'nao'
      WHEN p.status IS NULL THEN 'nao'
    END
  ) AS "Reembolso"
FROM cs_trading_order_shipping shipping
INNER JOIN cs_trading_order o ON o.id = shipping.order_id AND o.deleted_at IS NULL
INNER JOIN corporation_seller s ON s.id = shipping.seller_id
INNER JOIN corporation_company c ON c.id = s.company_id
LEFT JOIN (
  SELECT DISTINCT shipping_id
  FROM cs_trading_order_shipping_product
) sp ON sp.shipping_id = shipping.id
LEFT JOIN corporation_product_offer offer ON offer.id = sp.offer_id
LEFT JOIN corporation_product cp ON cp.id = offer.company_product_id
LEFT JOIN corporation_kit_offer ko ON ko.id = sp.kit_offer_id
LEFT JOIN corporation_catalog_kit kit ON ko.kit_id = kit.id
LEFT JOIN cs_trading_order_shipping_payment AS p ON p.shipping_id = shipping.id
WHERE date_format(o.date_created, '%%Y-%%m') = date_format(SUBDATE(NOW(), 1), '%%Y-%%m')
AND shipping.state NOT IN ('cancelled')
ORDER BY "data de criação do pedido" ASC;