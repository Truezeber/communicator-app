"use client";

import {
  Button,
  Field,
  Fieldset,
  Flex,
  Group,
  Input,
  Stack,
  Tabs,
} from "@chakra-ui/react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { CgUser, CgUserAdd } from "react-icons/cg";

const backendHomeUrl = "http://localhost:8000";

function Form() {
  const [spinning, setSpinning] = useState(false);

  const [lnumberError, setlnumberError] = useState("");
  const [lpasswordError, setlpasswordError] = useState("");

  const [numberError, setnumberError] = useState("");
  const [passwordError, setpasswordError] = useState("");
  const [rpasswordError, setrpasswordError] = useState("");
  const [nameError, setnameError] = useState("");
  const [surnameError, setsurnameError] = useState("");

  const router = useRouter();

  const [form_signin, setForm_signin] = useState({
    lnumber: null,
    lpassword: "",
  });

  const [form_signup, setForm_signup] = useState({
    number: null,
    password: "",
    rpassword: "",
    name: "",
    surname: "",
  });

  const saveJWT = (token: string) => {
    localStorage.setItem("JWT", token);
  };

  const signIn = async (number: number, password: string) => {
    const response = await fetch(`${backendHomeUrl}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        number: number,
        password: password,
      }),
    });

    const data = await response.json();
    console.log("Twój token:", data.access_token);
    return data;
  };

  const updateField_signin = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm_signin({
      ...form_signin,
      [e.target.name]: e.target.value,
    });
  };

  const updateField_signup = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm_signup({
      ...form_signup,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit_signin = async () => {
    if (form_signin.lnumber == null) {
      setlnumberError("Number is required");
      return;
    } else {
      setlnumberError("");
    }

    if (form_signin.lpassword === "") {
      setlpasswordError("Password is required");
      return;
    } else {
      setlpasswordError("");
    }

    setSpinning(true);
    console.log(`Form data: ${JSON.stringify(form_signin, null, 2)}`);
    await signIn(form_signin.lnumber, form_signin.lpassword).then(
      (tokenData) => {
        console.log("Cała odpowiedź:", tokenData);
      }
    );
    setSpinning(false);
  };

  const handleSubmit_signup = async () => {
    if (form_signup.number == null) {
      setnumberError("Number is required");
    } else {
      setnumberError("");
    }

    if (form_signup.password === "") {
      setpasswordError("Password is required");
    } else {
      setpasswordError("");
    }

    if (form_signup.password !== form_signup.rpassword) {
      setrpasswordError("Passwords needs to be the same");
    } else {
      setrpasswordError("");
    }

    if (form_signup.name === "") {
      setnameError("Name is required");
    } else {
      setnameError("");
    }

    if (form_signup.surname === "") {
      setsurnameError("Surname is required");
    } else {
      setsurnameError("");
    }

    console.log(`Form data: ${JSON.stringify(form_signup, null, 2)}`);
  };

  return (
    <Flex colorPalette="teal" suppressHydrationWarning>
      <Tabs.Root defaultValue="signin">
        <Tabs.List>
          <Tabs.Trigger value="signin">
            <CgUser />
            Sign In
          </Tabs.Trigger>
          <Tabs.Trigger value="signup">
            <CgUserAdd />
            Sign Up
          </Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="signin">
          <Fieldset.Root as="form" size="md" maxW="md">
            <Stack>
              <Fieldset.Legend>Sign In</Fieldset.Legend>
              <Fieldset.HelperText>Welcome back 👋</Fieldset.HelperText>
            </Stack>

            <Fieldset.Content>
              <Field.Root invalid={lnumberError !== ""}>
                <Field.Label>Number</Field.Label>
                <Input
                  name="lnumber"
                  type="number"
                  onChange={updateField_signin}
                />
                <Field.ErrorText>{lnumberError}</Field.ErrorText>
              </Field.Root>
              <Field.Root invalid={lpasswordError !== ""}>
                <Field.Label>Password</Field.Label>
                <Input
                  name="lpassword"
                  type="password"
                  onChange={updateField_signin}
                />
                <Field.ErrorText>{lpasswordError}</Field.ErrorText>
              </Field.Root>
              <Button loading={spinning} onClick={handleSubmit_signin}>
                Sign In
              </Button>
            </Fieldset.Content>
          </Fieldset.Root>
        </Tabs.Content>
        <Tabs.Content value="signup">
          <Fieldset.Root size="md" maxW="md">
            <Stack>
              <Fieldset.Legend>Sign Up</Fieldset.Legend>
              <Fieldset.HelperText>Introduce yourself 🤝</Fieldset.HelperText>
            </Stack>

            <Fieldset.Content>
              <Field.Root invalid={numberError !== ""}>
                <Field.Label>Number</Field.Label>
                <Input
                  name="number"
                  type="number"
                  onChange={updateField_signup}
                />
                <Field.ErrorText>{numberError}</Field.ErrorText>
              </Field.Root>
              <Group>
                <Field.Root invalid={nameError !== ""}>
                  <Field.Label>Name</Field.Label>
                  <Input name="name" onChange={updateField_signup} />
                  <Field.ErrorText>{nameError}</Field.ErrorText>
                </Field.Root>
                <Field.Root invalid={surnameError !== ""}>
                  <Field.Label>Surname</Field.Label>
                  <Input name="surname" onChange={updateField_signup} />
                  <Field.ErrorText>{surnameError}</Field.ErrorText>
                </Field.Root>
              </Group>
              <Field.Root invalid={passwordError !== ""}>
                <Field.Label>Password</Field.Label>
                <Input
                  name="password"
                  type="password"
                  onChange={updateField_signup}
                />
                <Field.ErrorText>{passwordError}</Field.ErrorText>
              </Field.Root>
              <Field.Root invalid={rpasswordError !== ""}>
                <Field.Label>Repeat password</Field.Label>
                <Input
                  name="rpassword"
                  type="password"
                  onChange={updateField_signup}
                />
                <Field.ErrorText>{rpasswordError}</Field.ErrorText>
              </Field.Root>
              <Button loading={spinning} onClick={handleSubmit_signup}>
                Sign Up
              </Button>
            </Fieldset.Content>
          </Fieldset.Root>
        </Tabs.Content>
      </Tabs.Root>
    </Flex>
  );
}

export default Form;
