CREATE OR REPLACE VIEW VW_PRODUCT_SYNC AS
with REQUISICOES(COD_ITEM, COD_FORNECEDOR, COD_EMPRESA, QTDE_OFICINA)
AS
(
  SELECT OS_REQUISICOES.COD_ITEM,
  OS_REQUISICOES.COD_FORNECEDOR,
  OS_REQUISICOES.COD_EMPRESA,
  SUM(OS_REQUISICOES.QUANTIDADE)
  FROM OS_REQUISICOES
  INNER JOIN OS ON OS.COD_EMPRESA = OS_REQUISICOES.COD_EMPRESA
    AND OS.NUMERO_OS = OS_REQUISICOES.NUMERO_OS
  WHERE
  (
    (OS.STATUS_OS = '0') OR
    ((OS.STATUS_OS = '1') AND (OS.DATA_ENCERRADA > SYSDATE))
  )
  AND OS_REQUISICOES.DATA <= SYSDATE
  GROUP BY
  OS_REQUISICOES.COD_ITEM,
  OS_REQUISICOES.COD_FORNECEDOR,
  OS_REQUISICOES.COD_EMPRESA
)
select
MV.COD_ITEM PRODUCTID,
 COALESCE(i.COD_ITEM, i.PART_NUMBER) as mpn,
  I.DESCRICAO name,
  MV.COD_FORNECEDOR,
  MV.COD_EMPRESA,
  i.COD_GTIN AS gtin,
  COALESCE (iff.preco_venda, IC.PRECO_VENDA, ic.custo_contabil) AS sellPrice,
  COALESCE(IC.PRECO_ORIGINAL, ih.CUSTO_MEDIO)  purchasePrice,
  COALESCE(IC.PRECO_MINIMO,ic.PRECO_VENDA) as listPrice,
  (COALESCE (E.QTDE, 0) -  COALESCE(E.RESERVADO, 0)) AS STOCK,
  COALESCE(E.RESERVADO, 0) AS securityGarageStock,
  COALESCE(R.QTDE_OFICINA,0) AS blockedGarageStock,
  fe.NOME_FORNECEDOR as brand,
  COALESCE(ih."DATA", TO_DATE('1986-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')) as updatedAt,
  CASE
     WHEN igi.DESCRICAO LIKE '%Pecas%' THEN 'PEÇAS'
     WHEN igi.DESCRICAO LIKE '%Acessorio%' THEN 'ACESSÓRIOS'
     WHEN igi.DESCRICAO LIKE '%Lubrificantes%' THEN 'LUBRIFICANTES'
     WHEN igi.DESCRICAO LIKE '%Pneus%' THEN 'PNEUS'
     ELSE igi.DESCRICAO
     END tipo_estoque,
SUBSTR(
    icc.DESCRICAO,
    INSTR(icc.DESCRICAO,'_')+1,
    LENGTH(icc.DESCRICAO)
    ) as category
from (
select coalesce(tb_qtd.cod_item, tb_val.cod_item) cod_item
,coalesce(tb_qtd.cod_empresa, tb_val.cod_empresa) cod_empresa
,coalesce(tb_qtd.cod_fornecedor, tb_val.cod_fornecedor) cod_fornecedor
, tb_val.sequencia seq_valor
, tb_qtd.sequencia seq_qtd
from
(select cod_item, cod_empresa, cod_fornecedor, max(sequencia) sequencia
from itens_historico ih1
where ih1.tipo_operacao in ('E', 'S')
group by cod_item, cod_empresa, cod_fornecedor) tb_qtd
full join
(select cod_item, cod_empresa, cod_fornecedor, max(sequencia) sequencia
from itens_historico ih1
where ih1.tipo_operacao in ('N')
group by cod_item, cod_empresa, cod_fornecedor) tb_val
on tb_qtd.cod_item = tb_val.cod_item and tb_qtd.cod_empresa = tb_val.cod_empresa and tb_qtd.cod_fornecedor = tb_val.cod_fornecedor) mv
left join estoque e on e.cod_item = mv.cod_item and e.cod_empresa = mv.cod_empresa and e.cod_fornecedor = mv.cod_fornecedor
inner join itens_custos ic on ic.cod_item = mv.cod_item and ic.cod_empresa = mv.cod_empresa and ic.cod_fornecedor = mv.cod_fornecedor
inner join itens_fornecedor iff on iff.cod_item = mv.cod_item and iff.cod_fornecedor = mv.cod_fornecedor
inner join itens_historico ih on case when mv.seq_valor > mv.seq_qtd then mv.seq_valor else mv.seq_qtd end = ih.sequencia
LEFT JOIN REQUISICOES R ON R.COD_ITEM = MV.COD_ITEM
    AND R.COD_FORNECEDOR = MV.COD_FORNECEDOR
  AND R.COD_EMPRESA = MV.COD_EMPRESA
INNER JOIN itens i ON i.COD_ITEM = mv.cod_item
LEFT JOIN FORNECEDOR_ESTOQUE fe ON fe.COD_FORNECEDOR = mv.COD_FORNECEDOR
INNER JOIN ITENS_GRUPO_INTERNO igi ON igi.COD_GRUPO_INTERNO = i.COD_GRUPO_INTERNO
INNER JOIN ITENS_CLASSE_CONTABIL icc ON icc.COD_CLASSE_CONTABIL = i.COD_CLASSE_CONTABIL
WHERE
i.STATUS in ('A','O')
AND igi.COD_GRUPO_INTERNO NOT IN (9)
AND mv.COD_EMPRESA in (33, 37, 41)
AND mv.COD_FORNECEDOR IN (12, 15, 17, 19, 20, 22)
