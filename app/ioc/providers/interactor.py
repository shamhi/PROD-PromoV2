from dishka import Provider, Scope, provide, provide_all

from app.interactors.antifraud import AntifraudInteractor
from app.interactors.auth import (
    OAuth2PasswordBearerUserInteractor,
    SignInBusinessCompanyInteractor,
    SignInUserInteractor,
    SignUpBusinessCompanyInteractor,
    SignUpUserInteractor,
)
from app.interactors.business import (
    CreateNewPromoInteractor,
    GetPromoByIdInteractor,
    GetPromosListInteractor,
    GetPromoStatByIdInteractor,
    PatchPromoByIdInteractor,
)
from app.interactors.caching import CacheAccessTokenInteractor, CacheAntifraudInteractor
from app.interactors.user import (
    AddCommentToPromoInteractor,
    AddLikeToPromoInteractor,
    DeleteLikeToPromoInteractor,
    DeleteUserCommentByIdInteractor,
    EditUserCommentByIdInteractor,
    GetPromoActivationsHistoryInteractor,
    GetPromoCommentByIdInteractor,
    GetPromoCommentsInteractor,
    GetUserProfileInteractor,
    GetUserPromoByIdInteractor,
    GetUserPromoFeedInteractor,
    PatchUserByIdInteractor,
    UserActivatePromoByIdInteractor,
)


class InteractorProvider(Provider):
    scope = Scope.REQUEST

    auth_interactor = provide_all(
        SignUpUserInteractor,
        SignInUserInteractor,
        SignUpBusinessCompanyInteractor,
        SignInBusinessCompanyInteractor,
    )

    business_interactor = provide_all(
        CreateNewPromoInteractor,
        GetPromosListInteractor,
        GetPromoByIdInteractor,
        PatchPromoByIdInteractor,
        GetPromoStatByIdInteractor,
    )

    user_interactor = provide_all(
        GetUserProfileInteractor,
        PatchUserByIdInteractor,
        GetUserPromoFeedInteractor,
        GetUserPromoByIdInteractor,
        AddLikeToPromoInteractor,
        DeleteLikeToPromoInteractor,
        AddCommentToPromoInteractor,
        GetPromoCommentsInteractor,
        GetPromoCommentByIdInteractor,
        EditUserCommentByIdInteractor,
        DeleteUserCommentByIdInteractor,
        UserActivatePromoByIdInteractor,
        GetPromoActivationsHistoryInteractor,
    )

    oauth2_interactor = provide(OAuth2PasswordBearerUserInteractor)
    cache_interactor = provide(CacheAccessTokenInteractor)
    caching_interactor = provide(CacheAntifraudInteractor)
    antifraud_interactor = provide(AntifraudInteractor)
