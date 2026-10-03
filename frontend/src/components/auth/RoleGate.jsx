import { useAuth } from "../../context/AuthContext";

function RoleGate({roles, children, fallback=null}) {
    const {user} = useAuth();
    return user && roles.includes(user?.role,) ? children : fallback;
}

export default RoleGate;