export function requireAuth(router: any) {
  const isDevBypass =
    process.env.NEXT_PUBLIC_BTA_DEV_BYPASS_LOGIN === "true";

  const isAuthenticated =
    sessionStorage.getItem("bta_authenticated") === "true";

  if (!isDevBypass && !isAuthenticated) {
    router.push("/login");
  }
}
