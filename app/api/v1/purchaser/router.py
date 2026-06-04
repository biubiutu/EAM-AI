from fastapi import APIRouter
from .quotation import QuotationRouter
from .contract import ContractRouter
from .supplier import SupplierRouter

router = APIRouter(prefix="/purchaser", tags=["采购端"])

router.include_router(QuotationRouter()._register_routes(), prefix="/quotation")
router.include_router(ContractRouter()._register_routes(), prefix="/contract")
router.include_router(SupplierRouter()._register_routes(), prefix="/supplier")
